import smtplib, ssl
import time
import yfinance as yf
import pandas as pd
import df_class

# use outlook app and put it in favorites by selecting the sender email address and clicking star in upper-right
# then set notifications for favorites

class EmailYahoo:



    def __init__(self):
        self.counter = 0
        self.buy_msg = "Buy today"
        self.df_short_table = df_class.Sample_DF_Call()

    def email_func(self):
        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = "jmzakatees@gmail.com"
        receiver_email = 'crudedecay@gmail.com'
        password = 'xxx'

        message = f'''\
        From: Javed Siddique {sender_email}
        To: Javed Siddique {receiver_email}
        Subject: {self.buy_msg}


        Dear Javed, This is the future:\
        {self.df_short_table.select_to_end}

        '''

        # send email here

        # Create a secure SSL context
        context = ssl.create_default_context()

        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()  # Can be omitted
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        except Exception as e:
            print('It did not work!')
            print(e)
        finally:
            server.quit()

    def trigger(self):
        x = 0
        while self.counter < 10:
            x = x + 1
            print(x)
            if x == 4:
                # self.buy_msg = f"Short that {x} mutha!"
                self.df_short_table.yahoo_sample()
                self.email_func()
                time.sleep(1)
                break
            else:
                time.sleep(2)
                self.counter += 1


def main():
    app = EmailYahoo()
    app.trigger()

if __name__ == "__main__":
    main()