from urllib import response

import requests
import csv
f = open(file='data.txt',mode='w',newline='',encoding='utf-8')
csv_writer = csv.DictWriter(f,fieldnames=['Nickname','sex','location','comment'])
headers={
    "cookie":"buvid3=4E7B50F4-496B-DBBD-91E3-2333668579CF06647infoc; b_nut=1720853706; _uuid=CEF93D2E-C219-1A59-2D86-739E49F1B2EC06519infoc; buvid_fp=318d6a316bbbcc3d42751cb96365c370; buvid4=69FDFBDD-2860-86C2-2364-D55DD150BAA707608-024071306-4hOitfgVZc1hsevqubcyFA%3D%3D; enable_web_push=DISABLE; home_feed_column=5; rpdid=|(k|k)u~km|k0J'u~k|)lJ~)J; DedeUserID=440521023; DedeUserID__ckMd5=6b865649632e1a18; header_theme_version=CLOSE; CURRENT_BLACKGAP=0; CURRENT_QUALITY=80; LIVE_BUVID=AUTO9917356671765102; browser_resolution=1659-941; bsource=search_bing; enable_feed_channel=DISABLE; SESSDATA=43c19f84%2C1756016046%2C486db%2A21CjA73kxLcYKRjEj_lIwJNGxCh-xSmnDZC0_0jg3bBPscta5k2pp1IeQf11YV-b9bupoSVjJ2Wm1oMldmUWFkcU14U3pEVXlVdUVNWl9CYlRlczkzUC1rX0pWalF2bnFsa1dYN18ySUFLVTFIWFhEeXR0aGdkWVl1a2tsZWhUV2xSMnc4Q0lzLTZBIIEC; bili_jct=1d07a626990f3a5ab2dcef3c83c88450; b_lsid=4AA14CAB_1953C331DE2; CURRENT_FNVAL=4048; sid=87tcpc2c; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDA3MzExMDIsImlhdCI6MTc0MDQ3MTg0MiwicGx0IjotMX0.O9WRNcYfG0Yxr2NBSv7oAIPd0oQwJpvhkshpRMxniow; bili_ticket_expires=1740731042",

    "user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36 Edg/133.0.0.0"
}
url = "https://api.bilibili.com/x/v2/reply/wbi/main?oid=113992777339059&type=1&mode=2&pagination_str=%7B%22offset%22:%22%22%7D&plat=1&seek_rpid=&web_location=1315875&w_rid=a0e4e98a91e3099aeaff87e4b91a25c0&wts=1740472782"
response = requests.get(url, headers=headers)
json_data=response.json()
print(json_data)
reply=json_data["data"]["replies"]
for i in reply:
    dit={
        'Nickname':i["member"]['uname'],
        'sex':i['member']['sex'],
        'location':i['reply_control']['location'].replace('IP属地： ',''),
        'comment':i['content']['message'],
    }
    print(dit)
    csv_writer.writerow(dit)