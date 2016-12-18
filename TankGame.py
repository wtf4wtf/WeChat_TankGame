#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, socket, urllib2, re, json
from urllib import urlencode, unquote
from random import randint
from hashlib import md5

socket.setdefaulttimeout(10)

OPEN_ID = None
RETRY_CONUT = 3
MSG_LIST = {
    "1000": u"请从微信或支付宝进入游戏！",
    "1001": u"亲，玩游戏请先绑定哦！",
    "1203": u"亲，您的积分不足，还是再赚些积分再来吧~",
    "1204": u"打了这么多坦克很累吧？休息一下，明天再来吧！",
    "1210": u"验证失败，请重新获取验证码！",
    "1211": u"验证码已过期啦，请重新获取验证号！",
    "2000": u"亲，服务器很忙，请稍后进入游戏！",
    "3001": u"无效的签名，请重新进入游戏！",
    "3004": u"亲，扣除（或增加）积分失败，请稍后重试哦！",
    "3005": u"打了这么多坦克很累吧？休息一下，明天再来吧！",
    "3006": u"请短信验证后继续游戏",
    "3007": u"亲，请文明、健康地进行游戏哦！",
    "3008": u"亲，请文明、健康地进行游戏哦！",
    "3009": u"我们的风险侦测系统发现您的信用卡账户通过非法的网络手段获取积分，为了您的个人信用记录请立即停止该种行为，同时我们可能需要您配合司法机关开展网络刑侦调查。如以上行为非您本人所为，请立即致电与我们联系。",
    "9999": u"亲，服务器很忙，请稍后进入游戏！"
}

def req(url, data=None, kw=[]):
    global MSG_LIST, RETRY_CONUT
    code = '9999'
    for i in range(RETRY_CONUT):
        try:
            resp = json.loads(urllib2.urlopen(url, data).read())
            code = str(resp['returnCode'])
            break
        except Exception, e:
            print 'Something wrong, wait for retry...'
            time.sleep(3) # sleep 3s
    if code == '0000':
        kws = []
        for k in kw:
            kws.append(str(resp[k]))
        return True, kws
    elif code in MSG_LIST.keys():
        return False, MSG_LIST[code]
    else:
        return False, 'Unknown error!'

def get_points():
    global OPEN_ID
    
    url = 'https://pointbonus.cmbchina.com/IMSPActivities/pointgames/queryPoints'
    data = urlencode({'openId': OPEN_ID, 'gameNo': '1', 'from': '161'})
    f, t = req(url, data, ['currentPoints'])
    if f == True:
        currentPoints = t[0]
        print 'The total points is: %s' % currentPoints
    else:
        print u'Query points failed, reason: %s'.encode('utf-8') % t

def play(score):
    global OPEN_ID

    # start
    url  = 'https://pointbonus.cmbchina.com/IMSPActivities/pointgames/decreasePoints'
    data = urlencode({'openId': OPEN_ID, 'gameNo': '1', 'from': '161'})
    f, t = req(url, data, ['serinalno'])
    if f == True:
        serinalno = t[0]
        print 'The game starts successfully, serinalno: %s' % serinalno
    else:
        print u'The game can not start, reason: %s'.encode('utf-8') % t
        return False

    # running
    print 'The game is playing, wait for %d seconds...' % (score * 2)
    time.sleep(score * 2)
    
    # end
    url  = 'https://pointbonus.cmbchina.com/IMSPActivities/pointgames/increasePoints'
    data = urlencode({'openId': OPEN_ID, 'gameNo': '1', 'from': '161', 'score': score, 'serinalno': serinalno, 'sign': md5(str(score) + 'CMBCHINA' + str(serinalno) + 'cmbchina').hexdigest()})
    f, t = req(url, data, ['totalScore'])
    if f == True:
        totalScore = t[0]
        print 'The game ends successfully, get %s points' % totalScore
    else:
        print u'The game can not end, reason: %s'.encode('utf-8') % t
        return False

    return True

def main():
    global OPEN_ID

    # setup
    try:
        OPEN_ID = unquote(raw_input(u'Please input the openId: '))
    except Exception, e:
        print 'OpenId error!'
        exit(-1)
    opener = urllib2.build_opener()
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_1_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13E238 MicroMessenger/6.2 NetType/WIFI Language/zh_CN'),
        ('Referer', 'https://pointbonus.cmbchina.com/IMSPActivities/pointgames/index?channel=161&timestamp=&state=&openid=%s&channel=WeiXin&signature=' % OPEN_ID),
        ('Origin', 'https://pointbonus.cmbchina.com'),
        ('Accept', 'application/json'),
        ('Accept-Language', 'zh-cn'),
        ('Connection', 'close')
    ]
    urllib2.install_opener(opener)

    # generate score list
    score_list = []
    for i in range(20):
        score_list.append(randint(0, 20))

    # play
    play_count = 0
    for score in score_list:
        play_count += 1
        print '========================================'
        print 'Game No.%d, random number: %d, %s'.encode('utf-8') % (play_count, score, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        status = play(score)
        if status:
            get_points()
        else:
            print 'Please read the tip above and run this program again!'
            exit(-1)
        time.sleep(5)

if __name__ == '__main__':
    main()
