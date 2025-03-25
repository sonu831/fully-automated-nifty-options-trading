import sys
from sys import argv
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    creds = {   
            "trading": True,
            "usr": argv[1],
            "pswd": argv[2],
            "pin": argv[3],
            "trade_watchlist": 7,
            "email": None
            }
except:
    # Get credentials from .env file
    creds = {   
        "trading": True,  
        "usr": os.getenv('ZERODHA_USER_ID'),
        "pswd": os.getenv('ZERODHA_PASSWORD'),
        "pin": None,  # We'll ask for this at runtime
        "trade_watchlist": 7,
        "email": os.getenv('ZERODHA_EMAIL')
        }
    
    # Ask for PIN at runtime
    if not creds["pin"]:
        creds["pin"] = input("Please enter your Zerodha PIN (OTP): ")
get_optimized_supertrend=False
#period=74
#multiplier=12.3
timeframe='5min'    #time period of chart
period=15     #period of supertrend
multiplier=14.2   #multiplier of supertrend
risk=500   #risk (this paramater goes from 50 to 1000 where 50 is lowest risk with low profits and losses where 1000 is highest risk with highest profits and losses, The number should be multiplier of 50 like 50,100,150,200 like that ...)
new_position_risk=150  #To continue the strategy after expiry , the risk to be taken paramater
new_position_halfrisk_or_not=True
target_price=0.95  #target price that you should exit when price hits target
qty=50 #lot size
qty_fixed_or_not=True
new_basket_name='algo'
how_refresh_every=12
uptrend_ce_or_pe='CE'
downtrend_ce_or_pe='CE'
headless=False
try:
    if get_optimized_supertrend:
        supt=open('/home/ubuntu/pycharmprojects/tradeautomation/optimized_supertrend_for_nifty.txt','r').read().split('\n')
        period=int(supt[0])
        multiplier=float(supt[1])
except:
    pass
from time import sleep
import pause
from math import floor
while True:
    try:
        import os 
        os.system('rm /home/ubuntu/pycharmprojects/tradeautomation/intimate.txt')    
        import warnings
        warnings.filterwarnings("ignore")
        #from click import option
        from kite.Brokers.Zerodha import *
        z = ZerodhaConnect(usr=creds, headless = headless)
        driver= z.subscribe()
        z.delete_all_kite()
        driver= z.subscribe()
        z.get_subscribed_ticker()
        funds=z.get_margins()['equity']['Available margin']
        if not qty_fixed_or_not and funds>37000:
            qty=100
            if funds>60000:
                qty=150
            if funds>80000:
                qty=200
        ########################################################################
        from login_fyers import *
        accounts,fyers=login_fyers()
        stock_name='NSE:NIFTY50-INDEX'
        name_script=name_to_script(stock_name)
        stock_name=name_script
        fyers.funds()
        l=full_data(accounts)
        #q=quote(accounts)
        #o=order(accounts)
        #data = l.full_data(stock_name)
        data=l.full_data(stock_name,resolution=5,days=98)
        data=data.resample(timeframe).ohlc().open.dropna()
        #############################################################
        from datetime import date, timedelta,datetime
        import calendar
        def thursday():
            now=datetime.datetime.now()
            Year=now.year
            A=calendar.TextCalendar(calendar.THURSDAY)
            thismonth=[]
            nextmonth=[]
            for b in range(now.month,now.month+2):
                thismonth=nextmonth.copy()
                nextmonth=[]
                for k in A.itermonthdays(Year,b):
                    if k!=0:
                        day=date(Year,b,k)
                        if day.weekday()==3:
                            #print("%s,%d-%d-%d" % (calendar.day_name[3] ,k,b,Year))
                            nextmonth.append(k)
            thismonth1=[]
            for i in range(len(thismonth)):
                if thismonth[i]>now.date().day:
                    thismonth1.append(thismonth[i])   
            thismonth=thismonth1          
            return thismonth,nextmonth

        def option_names(strike_price,ceorpe):
            thismonth,nextmonth=thursday()
            now=datetime.datetime.now()
            this=now.strftime('%b').upper()
            tt=now+timedelta(30)
            next=tt.strftime('%b').upper()
            this_name=[]
            for i in range(len(thismonth)):
                this_name.append(f'NIFTY {thismonth[i]}th w {this} {strike_price} {ceorpe}')
            this_name.pop()
            this_name.append(f'NIFTY {this} {strike_price} {ceorpe}')    
            next_name=[]
            for i in range(len(nextmonth)):
                next_name.append(f'NIFTY {nextmonth[i]}th w {next} {strike_price} {ceorpe}')
            next_name.pop()
            next_name.append(f'NIFTY {next} {strike_price} {ceorpe}')  
            this_name.extend(next_name)
            return this_name

        def select_strike_price(ltp):
            return round(ltp/50)*50

        def open_positions():
            bb=z.get_position()
            open_pos=dict()
            try:
                for i in bb:
                    if i!='totalpandl':
                        if bb[i]['product']!='CNC' and int(bb[i]['qty'])!=0:
                            open_pos[i]=bb[i]
        
                            #print(i)
            except:
                pass      
            return open_pos
        def is_option_active():
            try:
                global open_positions_list
                #o=open_positions().keys()
                o=open_positions_list.keys()
                for i in o:
                    if 'NIFTY' in i:
                        return True
            except Exception as error:
                print(error)
                return False            
            return False        

        def check_target(target=0.8):
            global open_positions_list
            open_pos=open_positions_list
            #open_pos=open_positions()
            #open_pos=open_positions()
            for i in open_pos:
                if i=='totalpandl':
                    continue
                
                if float(open_pos[i]['qty'])<0:
                    if float(open_pos[i]['avg'])*(1-target)>float(open_pos[i]['ltp']):
                        return True
                    else:
                        return False
            return False      

        def new_positions():
            if (old_trend=='down') :

                if int(now.strftime('%w'))>2 and int(now.strftime('%w'))<4:
                    symbol_sell=option_names(strike_price=select_strike_price(data.iloc[-2]['close']),ceorpe='PE')[1]
                    symbol_buy=option_names(strike_price=select_strike_price(data.iloc[-2]['close'])-risk,ceorpe='PE')[1]
                else:
                    symbol_sell=option_names(strike_price=select_strike_price(data.iloc[-2]['close']),ceorpe='PE')[0]
                    symbol_buy=option_names(strike_price=select_strike_price(data.iloc[-2]['close'])-risk,ceorpe='PE')[0]
                z.place_order(symbol=symbol_buy,qtn=50,transaction_type =ZC.TRANSACTION_TYPE_BUY) 
                #sleep(1)
                z.place_order(symbol=symbol_sell,qtn=50,transaction_type =ZC.TRANSACTION_TYPE_SELL)
                #sleep(1)

            if (old_trend=='up' ) :
                if int(now.strftime('%w'))>2 and int(now.strftime('%w'))<4:
                    symbol_sell=option_names(strike_price=select_strike_price(data.iloc[-2]['close']),ceorpe='CE')[1]
                    symbol_buy=option_names(strike_price=select_strike_price(data.iloc[-2]['close'])+risk,ceorpe='CE')[1]
                else:
                    symbol_sell=option_names(strike_price=select_strike_price(data.iloc[-2]['close']),ceorpe='CE')[0]
                    symbol_buy=option_names(strike_price=select_strike_price(data.iloc[-2]['close'])+risk,ceorpe='CE')[0]
                z.place_order(symbol=symbol_buy,qtn=50,transaction_type =ZC.TRANSACTION_TYPE_BUY) 
                #sleep(1)
                z.place_order(symbol=symbol_sell,qtn=50,transaction_type =ZC.TRANSACTION_TYPE_SELL)
                #sleep(1)

        def less_risk(risk):
            u=[]
            for i in range(1,100):
                u.append(50*i)
            u=np.array(u)
            yy=abs(u-(risk/2))
            mini=10000
            ind=0
            return u[np.argmin(yy)]

        def get_sleep_time():
            global timeframe
            if 'min' in timeframe:
                time_frame=int(timeframe[:-3])
            if 'h' in timeframe:
                time_frame=int(timeframe[:-1])
                time_frame=time_frame*60

            now = datetime.datetime.now()
            next_run = now.replace(minute=int(now.minute / time_frame) * time_frame, second=0, microsecond=0) + datetime.timedelta(minutes=time_frame)
            return next_run
        if new_position_halfrisk_or_not:
            half_risk=less_risk(risk)
        else:
            half_risk=risk
            

        overbought_or_oversold='oversold'

        def create_basket():
            global new_basket_name
            if driver.current_url!='https://kite.zerodha.com/orders/baskets':
                driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[2]/div[1]/a[2]/span').click()
                driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[1]/a[3]/span').click()
            try:
                driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div/section/div/div/span[1]/button').click()
            except:
                driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div/div/div[1]/button').click()
            driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[2]/div/form/div[1]/input').send_keys(new_basket_name)
            #sleep(2)
            u=False
            while True:
                try:
                    driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[2]/div/form/div[2]/button').click()
                    u=True
                    break
                except Exception as error:
                    print('trying agian to crate basket')
                    sleep(1)
                if u:
                    break    
            return True
        def name_to_price(stock_name):
            return re.sub(' ','',re.sub('[A-Z]','',stock_name[stock_name.find('w')+6:]))
        def add_instruments_basket(stock_names,market=True,qty=50,overnight=True,buy_sell=['buy','sell']):
            try:
                driver.find_element_by_xpath('/html/body/div[1]/form/section/footer/div[2]/button[2]').click()
            except:
                pass
            try:
                driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[2]/button').click()
            except:
                pass
            create_basket()
            co=0
            for stock_name in stock_names:
                strike_price=name_to_price(stock_name)
                try:
                    driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[1]/div/div/div/input').send_keys(strike_price)
                except:
                    sleep(5)
                    driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[1]/div/div/div/input').send_keys(strike_price)
                sleep(2)
                try:
                    for i in range(1,100):
                        s=driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[1]/div/ul/div/li[{i}]/span[1]/span').text
                        if s==stock_name:
                            driver.find_element_by_xpath(f'/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[1]/div/ul/div/li[{i}]/span[1]/span').click()
                            break
                except Exception as error:
                    print(error)
                if market==True:
                    driver.find_element_by_xpath('/html/body/div[1]/form/section/div[2]/div[2]/div[2]/div[2]/div/div[1]/label').click()
                for i in range(10):
                    driver.find_element_by_xpath('/html/body/div[1]/form/section/div[2]/div[2]/div[1]/div[1]/div/input').send_keys(Keys.BACKSPACE)                
                driver.find_element_by_xpath('/html/body/div[1]/form/section/div[2]/div[2]/div[1]/div[1]/div/input').send_keys(qty)
                if overnight==True:
                    driver.find_element_by_xpath('/html/body/div[1]/form/section/div[2]/div[1]/div/div[2]/label').click()
                if buy_sell[co]=='sell':
                    driver.find_element_by_xpath('/html/body/div[1]/form/header/div[1]/div[2]/div/div[2]/span/div/label').click()    
                co+=1
                driver.find_element_by_xpath('/html/body/div[1]/form/section/footer/div[2]/button[1]/span').click()
                #driver.find_element_by_xpath('/html/body/div[1]/form/section/footer/div[2]/button[2]').click()
            return True
        def check_margin(stock_names,market=True,overnight=True,close=True,buy_sell=['buy','sell']):
            global qty
            add_instruments_basket(stock_names,market,qty,overnight,buy_sell)
            sleep(2)
            margin=dict()
            try:
                margin['required_margin']=driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[1]/div/div[1]/div/span').text
            except:
                sleep(5)
                margin['required_margin']=driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[1]/div/div[1]/div/span').text
            margin['final_margin']=driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[1]/div/div[2]/div/span/span').text
            margin['final_margin']=float(re.sub('[,]','',margin['final_margin']))
            margin['required_margin']=float(re.sub('[,]','',margin['required_margin']))
            if close==True:
                driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[2]/button[2]').click()
            return margin

        def check_max_loss(stock_names,market=True,qty=qty,overnight=True,resistance=False):
            try:
                #stock_names=[symbol_buy,symbol_sell]
                margin=check_margin(stock_names,market=True,overnight=True,close=False)
                driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[1]/div/div[2]/a[1]/span').click()
                sleep(10)
                summary=dict()
                frame=driver.find_element_by_xpath('/html/body/div[1]/div[6]/div/div/div[2]/div/iframe')
                driver.switch_to.frame(driver.find_element_by_xpath('/html/body/div[1]/div[6]/div/div/div[2]/div/iframe'))
                t=driver.find_element_by_xpath('/html/body/div/div/div/div/div/div/div/div[1]/div[3]/div[2]/div/div').text.split('\n')
                summary=dict()
                for i in range(len(t)):
                    if i%2==0:
                        try:
                            y=t[i+1]
                            y=re.sub(',','',y)
                            y=re.sub('%','',y)
                            if y=='--':
                                y=None
                            summary[t[i]]=float(y)
                        except:
                            summary[t[i]]=t[i+1]  
                target=driver.find_element_by_xpath('/html/body/div/div/div/div/div/div/div/div[2]/div[3]/div/div[1]/div[2]/div[2]/div/div/input')
                if resistance!=False : 
                    for i in range(50):
                        target.send_keys(Keys.BACKSPACE)
                        target.send_keys(Keys.DELETE)
                        target.send_keys(Keys.BACKSPACE)
                    target.send_keys(resistance)
                    sleep(5)
                    s=driver.find_element_by_xpath('/html/body/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div')
                    n=s.text.split('\n')[-1]
                    projected_amount=int(re.sub('[^0-9]','',n))
                    summary['projected_amount']=projected_amount
                driver.get('https://kite.zerodha.com/orders/baskets')
                sleep(5)
                print(colored('#'.center(60,'#'),'yellow'))
                print(stock_names)
                print('Margin Required is :',margin)
                print('Summary is : ', summary)
                return summary,margin
            except Exception as error:
                print(error)
                driver.get('https://kite.zerodha.com/orders/baskets')
                sleep(5)
                try:
                    return summary,margin
                except :
                    pass
                #driver.find_element_by_xpath('/html/body/div/div/div/div/div/div/div/div[1]/div[3]/div[2]/div/div/div[1]/div[2]').text
                #driver.find_element_by_xpath('/html/body/div[1]/div[6]/div/div/div[3]/div/button').click()

        def basket_order(stock_names):
            print(colored(f'Trying to place the following orders {stock_names}',color='yellow'))
            margin=z.get_margins()
            fund= margin['equity']['Available margin']
            money=check_margin(stock_names,close=False)
            if float(money['required_margin'])>funds:
                #driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[2]/button[2]').click()
                global qty
                m.message('Margin is not enough in your account to trade... but trying to place order') 
            driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[2]/button[1]').click()
            driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/div/div/div[3]/div/button[1]').click()
            sleep(1)
            plac=driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[2]/div/table/tbody/tr[1]/td[8]/span/span').text
            #driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[2]/button[2]').click()
            try:
                driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[2]/button[2]').click()
            except:
                try:
                    driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[2]/button[2]').click()
                except:
                    pass   
                pass
            if plac=='FAILED':
                return False
            try:
                driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/div/div[2]/button[2]').click()
            except:
                pass
            return True  

        def clean_basket(all=False):
            global new_basket_name
            u=['/html/body/div[1]/div[1]/div/div[2]/div[1]/a[2]/span','/html/body/div[1]/div[2]/div[2]/div[1]/a[3]/span']
            for i in u:
                driver.find_element_by_xpath(i).click()
            try:
                if all==False:                  
                    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div/section/div/div/span[2]/div/input').send_keys(new_basket_name)
                    sleep(0.5)
                    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div/section/div/div/span[2]/div/input').send_keys(Keys.ENTER)
                for i in range(1,51):
                    el=driver.find_element_by_xpath(f'/html/body/div[1]/div[2]/div[2]/div[2]/div/section/div/table/tbody/tr[1]/td[1]')
                    #el.location_once_scrolled_into_view
                    name=el.text
                    if name!=False:
                        el=driver.find_element_by_xpath(f'/html/body/div[1]/div[2]/div[2]/div[2]/div/section/div/table/tbody/tr[1]/td[1]')
                        try:
                            hover = ActionChains(driver).move_to_element(el).perform()
                            #hover.perform()
                            sleep(2)
                            driver.find_element_by_class_name('context-menu').click()
                            sleep(1)
                            driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div/section/div/table/tbody/tr[1]/td[1]/div/ul/li[2]/a').click()
                            driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[3]/div/button[1]/span').click()
                        except:
                            pass 
            except:
                pass 
            sleep(1)     
            try:
                driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div/section/div/div/span[2]/span[2]').click() 
            except:
                pass    
            return True
       
        def get_strike_price(old_trend, new_trend,ce_or_pe,next=False,risk=risk):
            if old_trend=='down' and new_trend=='up':                        
                if (int(now.strftime('%w'))>=2 and int(now.strftime('%w'))<4) or next==True:
                    symbol_sell=option_names(strike_price=select_strike_price(data.iloc[-2]['close']),ceorpe=ce_or_pe)[1]
                    symbol_buy=option_names(strike_price=select_strike_price(data.iloc[-2]['close'])-risk,ceorpe=ce_or_pe)[1]
                else:
                    symbol_sell=option_names(strike_price=select_strike_price(data.iloc[-2]['close']),ceorpe=ce_or_pe)[0]
                    symbol_buy=option_names(strike_price=select_strike_price(data.iloc[-2]['close'])-risk,ceorpe=ce_or_pe)[0]
            if (old_trend=='up' and new_trend=='down') :
                if (int(now.strftime('%w'))>=2 and int(now.strftime('%w'))<4) or next==True:
                    symbol_sell=option_names(strike_price=select_strike_price(data.iloc[-2]['close']),ceorpe=ce_or_pe)[1]
                    symbol_buy=option_names(strike_price=select_strike_price(data.iloc[-2]['close'])+risk,ceorpe=ce_or_pe)[1]
                else:
                    symbol_sell=option_names(strike_price=select_strike_price(data.iloc[-2]['close']),ceorpe=ce_or_pe)[0]
                    symbol_buy=option_names(strike_price=select_strike_price(data.iloc[-2]['close'])+risk,ceorpe=ce_or_pe)[0]
            return [symbol_buy,symbol_sell]   
        def get_best_strike_price(old_trend,new_trend):
            global uptrend_ce_or_pe
            global downtrend_ce_or_pe
            if old_trend=='down' and new_trend=='up':  
                ceorpe=uptrend_ce_or_pe
            if old_trend=='up' and new_trend=='down':
                ceorpe=downtrend_ce_or_pe
            return get_strike_price(old_trend,new_trend,ceorpe)           

        def best_option_selection(next=False,resistance_up=False,resistance_down=False,risk=risk):
            global uptrend_ce_or_pe
            global downtrend_ce_or_pe
            global qty
            up_pe,margin_up_pe=check_max_loss(get_strike_price('down','up','PE',next,risk=risk),market=True,qty=qty,overnight=True,resistance=resistance_up)
            up_ce,margin_up_ce=check_max_loss(get_strike_price('down','up','CE',next,risk=risk),market=True,qty=qty,overnight=True,resistance=resistance_up)  
            down_pe,margin_down_pe=check_max_loss(get_strike_price('up','down','PE',next,risk=risk),market=True,qty=qty,overnight=True,resistance=resistance_down) 
            down_ce,margin_down_ce=check_max_loss(get_strike_price('up','down','CE',next,risk=risk),market=True,qty=qty,overnight=True,resistance=resistance_down)            
            r=False
            try:
                if abs(up_pe['projected_amount'])>abs(up_ce['projected_amount']):
                    uptrend_ce_or_pe='CE'
                    qty_check(margin=margin_up_ce['required_margin'])
                if abs(up_pe['projected_amount'])<abs(up_ce['projected_amount']): 
                    uptrend_ce_or_pe='PE'
                    qty_check(margin=margin_up_pe['required_margin'])
            except:
                if abs(up_pe['Max Loss'])>abs(up_ce['Max Loss']):
                    uptrend_ce_or_pe='CE'
                    qty_check(margin=margin_up_ce['required_margin'])
                if abs(up_pe['Max Loss'])<abs(up_ce['Max Loss']): 
                    uptrend_ce_or_pe='PE'
                    qty_check(margin=margin_up_pe['required_margin'])
            try:
                
                if abs(down_pe['projected_amount'])>abs(down_ce['projected_amount']):
                    downtrend_ce_or_pe='CE'
                    qty_check(margin=margin_down_ce['required_margin'])
                if abs(down_pe['projected_amount'])<abs(down_ce['projected_amount']):
                    downtrend_ce_or_pe='PE' 
                    qty_check(margin=margin_down_pe['required_margin'])
            except:
                if abs(down_pe['Max Loss'])>abs(down_ce['Max Loss']):
                    downtrend_ce_or_pe='CE'
                    qty_check(margin=margin_down_ce['required_margin'])
                if abs(down_pe['Max Loss'])<abs(down_ce['Max Loss']):
                    downtrend_ce_or_pe='PE' 
                    qty_check(margin=margin_down_pe['required_margin'])
            return uptrend_ce_or_pe,downtrend_ce_or_pe   
        def refresh_every(count):
            global how_refresh_every
            if count/how_refresh_every==round(count/how_refresh_every):
                return True
            else:
                return False
        def qty_check(old_trend=None,margin=None):
            global qty
            global qty_fixed_or_not
            if margin==None:
                if old_trend=='up' or old_trend==None:
                    u=check_margin(get_best_strike_price('up','down'))['required_margin']
                    q=u
                sleep(2)
                try:
                    if old_trend=='down' or old_trend==None:
                        v=check_margin(get_best_strike_price('down','up'))['required_margin']
                        q=v
                except:
                    sleep(10)
                    v=check_margin(get_best_strike_price('down','up'))['required_margin']  
                    q=v
            else:
                u=margin
                v=margin          
            if old_trend==None:
                q=max(u,v)
            f=z.get_margins()['equity']['Available margin']
            newqty=floor(f/q)*50
            if qty>newqty:
                qty=newqty
            if not qty_fixed_or_not:
                qty=newqty
            if qty==0:
                qty=50
            return qty

        def refresh():
            global resistance_up
            global resistance_down
            print()
            print(colored('Refreshing'.center(50,'-'),'yellow'))
            clean_basket()
            best_option_selection(resistance_up=resistance_up,resistance_down=resistance_down)
            print('UP Trend : ',get_best_strike_price('down','up'))
            print('Down Trend : ',get_best_strike_price('up','down'))
            print("Updated Quantity is :",qty)
        def position_trend():
            global open_positions_list
            try:
                strike=[]
                buyorsell=[]
                for i in open_positions_list:
                    strike.append(int(name_to_price(i)))
                    buyorsell.append(int(open_positions_list[i]['qty']))
                if buyorsell[strike.index(min(strike))]>0 and buyorsell[strike.index(max(strike))]<0:
                    return 'up'
                if buyorsell[strike.index(min(strike))]<0 and buyorsell[strike.index(max(strike))]>0:
                    return 'down'   
            except :
                return False                 
        def which_week():
            global open_positions_list
            a=open_positions_list.keys()
            #a=['NIFTY 24th w MAR 16800 CE', 'NIFTY 24th w MAR 17300 CE']
            date=[]
            month=[]
            for y in a:
                u=re.sub('[^0-9]',' ',y).split(' ')
                for i in u:
                    if len(i)>0:
                        date.append(i)
                        break
            for y in a:
                for i in y.split(' '):
                    if len(i)==3 :
                        month.append(i)    
            return list(zip(date,month,list(a)))            
        def is_today_expiry():
            a=which_week()
            pos=[]
            for i,j,k in a:
                if i==datetime.datetime.now().strftime('%d'):
                    if j==datetime.datetime.now().strftime('%h').upper():
                        pos.append(k)
            if int(datetime.datetime.now().strftime('%w'))==4:
                for i in a :
                    if datetime.datetime.now().strftime('%b').upper() in i:
                        if datetime.datetime.now().strftime('%b').upper() != (datetime.datetime.now()+datetime.timedelta(days=7)).strftime('%b').upper():
                            pos.append(i[-1])
                
            #if int(datetime.datetime.now().strftime('%w'))==4:
            #    return True 
            if len(pos)==0:
                return False
            else:
                return pos
        def exit_i(i):
            driver.find_element_by_xpath(f'/html/body/div[1]/div[2]/div[2]/div/div/section[1]/div/div/table/tbody/tr[{i}]/td[1]/div/label/span').click()

        def final_exit_button():
            driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/section[1]/div/div/table/tfoot/tr/td[1]/button').click()
            driver.find_element_by_xpath('/html/body/div[1]/div[5]/div/div/div/div[3]/div/div/button[1]').click()
        def list_open_nifty_options():
            global open_positions_list
            lis=[]
            for i in open_positions_list:
                if i[0:5]=='NIFTY':
                    lis.append(i)
            return lis
        def exit_nifty_options():
            lis=list_open_nifty_options()
            exit_positions(lis)
            
        
        def exit_positions(to_exit):
            driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[2]/div[1]/a[4]/span').click()
            for i in range(2):
                driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/section[1]/div/div/table/thead/tr/th[1]/div/label/span').click()
            sleep(0.1)
            #to_exit=['NIFTY 17th w MAR 16400 PE','NIFTY 17th w MAR 16500 PE']
            #driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[2]/div/div/section[1]/div/div/table/thead/tr/th[1]/div/label/span').click()
            try:
                for i in range(1,10000):
                    stock_driver=driver.find_element_by_xpath(f'/html/body/div[1]/div[2]/div[2]/div/div/section[1]/div/div/table/tbody/tr[{i}]/td[3]/span[1]')
                    u=stock_driver.text
                    print(u)
                    if u in to_exit:
                        exit_i(i)
            except:
                pass
            try:
                final_exit_button()
            except:
                pass
                    
            
        
        resistance_up=False
        resistance_down=False
        import datetime
        data=l.full_data(stock_name,resolution=5,days=98)
        data=data.resample(timeframe).ohlc().open.dropna()
        supertrend_value=SuperTrend(data,period,multiplier)
        old_trend=supertrend_value[f'STX_{period}_{multiplier}'].iloc[-3]
        new_trend=supertrend_value[f'STX_{period}_{multiplier}'].iloc[-2] 
        tren=supertrend_value[f'STX_{period}_{multiplier}'].iloc[-1] 
        resistance_up=False
        resistance_down=False
        if tren=='up':
            resistance_up=supertrend_value[f'ST_{period}_{multiplier}'].iloc[-1] 
            resistance_up=round(resistance_up)
        else:
            resistance_down=supertrend_value[f'ST_{period}_{multiplier}'].iloc[-1] 
            resistance_down=round(resistance_down)        
        print(colored('#'.center(60,'#'),'yellow'))
        open_positions_list=open_positions()
        print(f'Open positions are : {open_positions_list}')
        clean_basket()
        best_option_selection(risk=risk,resistance_up=resistance_up,resistance_down=resistance_down)
        print('UP Trend : ',get_best_strike_price('down','up'))
        print('Down Trend : ',get_best_strike_price('up','down'))
        print("Updated Quantity is :",qty)
        #refresh()
        #qty_check()
        count=0
        sleep(2)
        while True:
            count+=1
            #try:
            #sleep(2)
            if ((0 <= time.localtime().tm_wday <= 4) and (datetime.datetime.strptime(
                            datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y") + " 09:15:01",
                            "%d-%m-%Y %H:%M:%S") <= datetime.datetime.now() <= datetime.datetime.strptime(
                        datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y") + " 15:30:00",
                        "%d-%m-%Y %H:%M:%S"))):        
                data=l.full_data(stock_name,resolution=5,days=98)
                data=data.resample(timeframe).ohlc().open.dropna()
                #data=l.full_data(stock_name,resolution=5,days=98)
                supertrend_value=SuperTrend(data,period,multiplier)
                old_trend=supertrend_value[f'STX_{period}_{multiplier}'].iloc[-3]
                new_trend=supertrend_value[f'STX_{period}_{multiplier}'].iloc[-2]      
                tren=supertrend_value[f'STX_{period}_{multiplier}'].iloc[-1] 
                if tren=='up':
                    resistance_up=supertrend_value[f'ST_{period}_{multiplier}'].iloc[-1] 
                    resistance_up=round(resistance_up)
                else:
                    resistance_down=supertrend_value[f'ST_{period}_{multiplier}'].iloc[-1] 
                    resistance_down=round(resistance_down)   
                print(colored('*'.center(50,'*'),'cyan'))
                print(colored(datetime.datetime.now().strftime('%H:%M:%S'),'red'))
                print (colored(f"Open is :{data.iloc[-2]['open']}", 'yellow'))
                print (colored(f"High is :{data.iloc[-2]['high']}", 'yellow'))
                print (colored(f"Low is :{data.iloc[-2]['low']}", 'yellow'))
                print (colored(f"Close is :{data.iloc[-2]['close']}", 'yellow'))
                print(colored(f"Old trend is : {old_trend}",'yellow'))
                print(colored(f"New trend is : {new_trend}",'yellow'))
                open_positions_list=open_positions()
                print(colored(f'Open positions are : {open_positions_list}','yellow'))
                pt=position_trend()
                
                if (old_trend=='down' and new_trend=='up') and pt!='up' :
                    try:
                        #z.exit_all_positions()
                        exit_nifty_options()
                    except Exception as error:
                        print(error)
                    options_list=get_best_strike_price(old_trend='down', new_trend='up')
                    basket_order(options_list)
                if (old_trend=='up' and new_trend=='down') and pt!='down' :
                    try:
                        #z.exit_all_positions()
                        exit_nifty_options()
                    except Exception as error:
                        print(error)
                    options_list=get_best_strike_price(old_trend='up', new_trend='down')
                    basket_order(options_list)
                if pt=='up' and (new_trend=='down'):
                    try:
                        #z.exit_all_positions()
                        exit_nifty_options()
                        open_positions()
                    except Exception as error:
                        print(error)          
                if pt=='down' and (new_trend=='up'):
                    try:
                        #z.exit_all_positions()
                        exit_nifty_options()
                    except Exception as error:
                        print(error)        
                #target_price=0.1  
                if check_target(target_price):
                    m.message(f'trying to exit all positions as given target {target_price*100} reached ')
                    #z.exit_all_positions()
                    exit_nifty_options()
                    #new_positions()
                if not is_option_active():   
                    if abs(supertrend_value[f'ST_{period}_{multiplier}'].iloc[-2]-data.iloc[-2]['close'])<new_position_risk:
                        if (new_trend=='down') :
                            options_list=get_best_strike_price(old_trend='up', new_trend='down')
                            basket_order(options_list)
                        if (new_trend=='up' ) :
                            options_list=get_best_strike_price(old_trend='down', new_trend='up')
                            basket_order(options_list)
                if ((0 <= time.localtime().tm_wday <= 4) and (datetime.datetime.strptime(
                                datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y") + " 15:19:55",
                                "%d-%m-%Y %H:%M:%S") <= datetime.datetime.now() <= datetime.datetime.strptime(
                            datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y") + " 15:29:00",
                            "%d-%m-%Y %H:%M:%S"))):
                            td=is_today_expiry()
                            print("checking if any positions left to expiry ... if so i will close them ! ")
                            if td!=False:
                                print("Trying to exit today expiry positions : ", td)
                                #exit_nifty_options()
                                exit_positions(td)
                                

                if refresh_every(count):
                    refresh()  

                if ((0 <= time.localtime().tm_wday <= 4) and (datetime.datetime.strptime(
                                datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y") + " 15:29:55",
                                "%d-%m-%Y %H:%M:%S") <= datetime.datetime.now() <= datetime.datetime.strptime(
                            datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y") + " 15:40:00",
                            "%d-%m-%Y %H:%M:%S"))):
                    import sys
                    sys.exit()                       
                pause.until(get_sleep_time())
                sleep(1)
            else:
                print('Market is yet to open...')
                sleep(1)
                if ((0 <= time.localtime().tm_wday <= 4) and (datetime.datetime.strptime(
                                datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y") + " 15:29:55",
                                "%d-%m-%Y %H:%M:%S") <= datetime.datetime.now() <= datetime.datetime.strptime(
                            datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y") + " 15:41:00",
                            "%d-%m-%Y %H:%M:%S"))):
                    clean_basket()
                    import sys
                    sys.exit() 
            
    except Exception as error:
        m.message("There is some error in whole code , please verify ....")
        m.message(error)
        sleep(5)
