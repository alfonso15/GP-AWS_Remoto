import datetime
from typing import Dict
from sentry_sdk import capture_exception
from tickets.models import Ticket, SerialNumber
from .client import SQLHandler


class CreateTicketHandler(SQLHandler):

    def create_ticket(self, ticket: Ticket, ):
        ticket.attempts += 1
        ticket.error_detail = ''
        ticket.save()

        if not ticket.report_id:
            call_number, count = None, 0
            while (count < 3) and call_number is None:
                try:
                    call_number = self._get_call_number()
                except Exception as e:
                    count += 1
                    if count >= 3:
                        ticket.error_detail = "Failed to generate call number"
                        raise e
        else:
            call_number = ticket.report_id

        data = {
            'CALLNBR': call_number,
            'CUSTNMBR': str(ticket.company.customer_number),
            'Customer_Reference': ticket.full_name[:20],
            'SVCDESCR': ticket.description,
            **self._initial_configuration(),
            **self._get_serial_number_data(ticket),
            **self._get_fixed_fields(),
            **self._get_price_level_data(ticket.company.customer_number),
            **self._get_dates_data(),
        }

        data.update(self._get_address_data(ticket.company.customer_number, data.get('ADRSCODE')))
        data.update(self._get_contract_data(data, ticket))

        keys_str, values_str = self._format_data(data)

        if not ticket.insert_200:
            self.cursor.execute(f"INSERT INTO SVC00200 ({keys_str}) VALUES ({values_str})")
            self.conn.commit()

            ticket.report_id = call_number
            ticket.insert_200 = True
            ticket.status = data.get('SRVSTAT')
            ticket.save()

        data_201 = {
            'SRVRECTYPE': data.get('SRVRECTYPE'),
            'CALLNBR': call_number,
            'LNITMSEQ': 1,
            'EQUIPID': ticket.serial_number_id,
            'ITEMNMBR': ticket.serial_number_instance.itemnmbr,
            'PROBCDE': ticket.failure_instance.probcde,
            'Note_Index_1': 0,
            'Note_Index_2': 0,
            'Note_Index_3': 0,
        }

        keys_str, values_str = self._format_data(data_201)

        if not ticket.insert_201:
            self.cursor.execute(f"INSERT INTO SVC00201 ({keys_str}) VALUES ({values_str})")
            self.conn.commit()

            ticket.insert_201 = True
            ticket.save()

        data_202 = {
            'SRVRECTYPE': data.get('SRVRECTYPE'),
            'CALLNBR': call_number,
            'EQPLINE': 1,
            'EQUIPID': ticket.serial_number_id,
            'ITEMNMBR': ticket.serial_number_instance.itemnmbr,
            'METER1': 0,
            'METER2': 0,
            'METER3': 0,
            'LSTDTEDT': '00:00.0',
            'PMPERF': 0
        }

        keys_str, values_str = self._format_data(data_202)

        if not ticket.insert_202:
            self.cursor.execute(f"INSERT INTO SVC00202 ({keys_str}) VALUES ({values_str})")
            self.conn.commit()

            ticket.insert_202 = True
            ticket.save()

        if not ticket.insert_SY03900:
            try:
                self._register_comment_data(ticket)
            except Exception as e:
                error_message = f"Error Hot Line: {str(e)}; "
                ticket.error_detail += error_message
                ticket.save()

            try:
                self._update_comment_data(ticket)
            except Exception as e:
                error_message = f"Error Hot Line: {str(e)}; "
                ticket.error_detail += error_message
                ticket.save()

        try:
            self._register_email_and_names(call_number, ticket.email)
        except Exception as e:
            error_message = f"Error Emails: {str(e)}; "
            ticket.error_detail += error_message
            ticket.save()

    def _format_data(self, data):
        keys_str = ''
        values_str = ''
        for key, value in data.items():
            if value is not None:
                keys_str += key + ', '
                if type(value) == str:
                    value = f"'{value.strip()}'"
                elif type(value) == datetime.datetime:
                    value = f"'{value}'"
                values_str += f"{value}, "
        return keys_str[:-2], values_str[:-2]

    def _get_call_number(self):
        sql = "BEGIN DECLARE @stored_proc_name char(27) DECLARE @retstat int DECLARE @param1 char(255) set nocount on SELECT @stored_proc_name = 'dbo.SVC_New_Call_Number' EXEC @retstat = @stored_proc_name @param1 OUT SELECT @retstat, @param1 set nocount on END"

        self.cursor.execute(sql)
        query = self.cursor.fetchone()
        return query[1]

    def _get_dates_data(self):
        return {
            "ENTDTE": datetime.date.today().strftime("%Y-%m-%d 00:00:00.000"),
            "ENTTME": datetime.datetime.now().strftime("1900-01-01 %H:%M:%S.000"),
            "Notify_Date": "1900-01-01 00:00:00.000",
            "Notify_Time": "1900-01-01 00:00:00.000",
            "ETADTE": "1900-01-01 00:00:00.000",
            "ETATME": "1900-01-01 00:00:00.000",
            "DISPDTE": "1900-01-01 00:00:00.000",
            "DISPTME": "1900-01-01 00:00:00.000",
            "ARRIVDTE": "1900-01-01 00:00:00.000",
            "ARRIVTME": "1900-01-01 00:00:00.000",
            "COMPDTE": "1900-01-01 00:00:00.000",
            "COMPTME": "1900-01-01 00:00:00.000",
            "Response_Date": "1900-01-01 00:00:00.000",
            "Response_Time": "1900-01-01 00:00:00.000",
        }

    def _initial_configuration(self):
        self.cursor.execute("EXEC dbo.zDP_SVC00998F_1 NULL,NULL")
        query = self.cursor.fetchone()
        return {
            'SRVRECTYPE': query.SRVRECTYPE,
            'SRVSTAT': query.SRVSTAT,
        }

    def _get_serial_number_data(self, ticket):
        self.cursor.execute(f"EXEC dbo.zDP_SVC00300SS_5 {ticket.serial_number_id}")
        query = self.cursor.fetchone()

        data = {
            'serial_number': query.SERLNMBR,
            'adrscode': query.ADRSCODE,
            'offid': query.OFFID,
            'svcarea': query.SVCAREA,
            'techid': query.TECHID,
            'timezone': query.TIMEZONE,
            'itemnmbr': query.ITEMNMBR,
        }
        serial, _ = SerialNumber.objects.get_or_create(serial_number_id=query.EQUIPID, company=ticket.company, defaults=data)
        ticket.serial_number_instance = serial
        ticket.save()

        data.pop('serial_number')
        data.pop('itemnmbr')

        return {key.upper(): str(value) for key, value in data.items()}

    def _get_fixed_fields(self):
        zero_fields = ['LABSTOTPRC', 'LABPCT', 'LABSTOTCST', 'PARSTOTPRC', 'PARTPCT', 'PARSTOTCST', 'MSCSTOTPRC',
                       'MISCPCT', 'MISSTOTCST', 'PRETAXTOT', 'TAXAMNT', 'TOTAL', 'Invoiced_Amount', 'METER1',
                       'METER2', 'METER3']
        data = {field: 0 for field in zero_fields}
        data['Print_to_Web'] = 1
        return data

    def _get_address_data(self, customer_number, address_code) -> Dict:
        """Table RM00102"""
        self.cursor.execute(f"EXEC dbo.zDP_RM00102SS_1 {customer_number}, '{address_code}'")
        query = self.cursor.fetchone()
        # March 23, errors raised due to query returning None in this step, bypass data to avoid error
        if query is None:
            return {}
        return {
            'ADDRESS1': query.ADDRESS1,
            'ADDRESS2': query.ADDRESS2,
            'ADDRESS3': query.ADDRESS3,
            'CITY': query.CITY,
            'STATE': query.STATE,
            'ZIP': query.ZIP,
            'CNTCPRSN': query.CNTCPRSN,
            'PHONE1': query.PHONE1,
            'COUNTRY': query.COUNTRY,
        }

    def _get_price_level_data(self, customer_number):
        """Table RM00102"""
        self.cursor.execute(
            f"SELECT CUSTNMBR, CUSTNAME, PYMTRMID, SLPRSNID, PRCLEVEL FROM RM00101 WHERE CUSTNMBR = {customer_number}")
        query = self.cursor.fetchone()

        return {
            'CUSTNAME': query.CUSTNAME[:62],
            'PYMTRMID': query.PYMTRMID,
            'SLPRSNID': query.SLPRSNID,
            'PRICELVL': query.PRCLEVEL,
        }

    def _get_contract_data(self, data, ticket):
        try:
            customer_number = data.get('CUSTNMBR').strip()
            adrscode = data.get('ADRSCODE').strip()
            date = datetime.date.today().strftime("%Y.%m.%d")
            item_number = ticket.serial_number_instance.itemnmbr
            sql = "BEGIN DECLARE @stored_proc_name char(37) DECLARE @retstat int DECLARE @param6 smallint DECLARE @param7 char(11) DECLARE @param8 numeric(19,5) set nocount on " \
                "SELECT @stored_proc_name = 'dbo.SVC_Find_Active_Contract_Line'" \
                f"EXEC @retstat = @stored_proc_name {customer_number}, '{adrscode}', {ticket.serial_number_id}, '{item_number}', '{date}', @param6 OUT, @param7 OUT, @param8 OUT SELECT @retstat, @param6, @param7, @param8 set nocount on END"

            self.cursor.execute(sql)
            query = self.cursor.fetchone()

            self.cursor.execute(f"SELECT * FROM SVC00600 WHERE CONTNBR = {query[2]}")
            query = self.cursor.fetchone()

            fields = ['CONSTS', 'CONTNBR', 'Bill_To_Customer', 'CURNCYID', 'SRVTYPE', 'priorityLevel', 'TAXSCHID',
                      'TAXEXMT1', 'TAXEXMT2', 'PORDNMBR', 'SVC_Bill_To_Address_Code', 'CURRNIDX', 'XCHGRATE', 'EXCHDATE',
                      'DECPLACS', 'TIME1', 'RATECALC', 'VIEWMODE', 'ISMCTRX', 'EXPNDATE', 'DENXRATE', 'MCTRXSTT']

            return {f: getattr(query, f) for f in fields}
        except Exception as e:
            capture_exception(e)
            return {}

    def _register_comment_data(self, ticket):
        self.cursor.execute(
            f"SELECT NOTEINDX FROM SVC00200 WHERE CALLNBR = {ticket.report_id}")
        query = self.cursor.fetchone()
        noteindx = query.NOTEINDX

        ticket.error_detail = f"NOTEINDX {noteindx}"

        data = {
            "NOTEINDX": noteindx,
            "TXTFIELD": ticket.comments,
        }
        keys_str, values_str = self._format_data(data)

        self.cursor.execute(f"INSERT INTO SY03900 ({keys_str}) VALUES ({values_str})")
        self.conn.commit()

        ticket.insert_SY03900 = True
        ticket.save()

    def _update_comment_data(self, ticket):
        self.cursor.execute(
            f"SELECT NOTEINDX FROM SVC00200 WHERE CALLNBR = {ticket.report_id}")
        query = self.cursor.fetchone()
        noteindx = query.NOTEINDX

        ticket.error_detail = f"NOTEINDX {noteindx}"

        self.cursor.execute(f"UPDATE SY03900 SET TXTFIELD='{ticket.comments}' "
                            f"WHERE NOTEINDX='{noteindx}'")
        self.conn.commit()
        ticket.insert_SY03900 = True
        ticket.error_detail += " [U]"
        ticket.save()

    """
    Este metodo es usado por el command 'create_comments' que ejecuta un cron cada N minutos
    """
    def _register_or_update_comment_data(self, ticket):
        """
        ToDo: debugear este metodo para que sea el estandar
        """
        # get ticket from sqlsever
        self.cursor.execute(
            f"SELECT NOTEINDX FROM SVC00200 WHERE CALLNBR = {ticket.report_id}")
        query = self.cursor.fetchone()
        noteindx = query.NOTEINDX

        ticket.error_detail = f"NOTEINDX {noteindx}"

        # Validate if comment exists in table SY03900
        self.cursor.execute(
            f"SELECT NOTEINDX FROM SY03900 WHERE NOTEINDX = {noteindx}")
        query_comment = self.cursor.fetchall()

        if not ticket.comments:
            return False  # blank comment breaks this flow

        if not query_comment:  # comment not exists, create new one
            data = {
                "NOTEINDX": noteindx,
                "TXTFIELD": ticket.comments,
            }
            keys_str, values_str = self._format_data(data)
            sql_query = f"INSERT INTO SY03900 ({keys_str}) VALUES ({values_str})"

            self.cursor.execute(sql_query)
            self.conn.commit()

            ticket.insert_SY03900 = True
            ticket.error_detail += " [Comment Created]"
            ticket.save()
        else:  # comment exists, update
            self.cursor.execute(f"UPDATE SY03900 SET TXTFIELD='{ticket.comments}' "
                                f"WHERE NOTEINDX='{noteindx}'")
            self.conn.commit()
            ticket.insert_SY03900 = True
            ticket.error_detail += " [Comment Updated]"
            ticket.save()

        return True  # True only if flow is completed

    def _register_email_and_names(self, call_number, email):

        self.cursor.execute(f"UPDATE zSV00200 SET INET1='{email}', INET2='{email}' "
                            f"WHERE CALLNMBR='{call_number}'")
        self.conn.commit()
