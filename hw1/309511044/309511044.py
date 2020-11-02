import requests
from bs4 import BeautifulSoup
import time
import sys

#cookie資料
payload = {
    "yes" : "yes"
}
rs = requests.session() #save information in one cookie
rs.post("https://www.ptt.cc/ask/over18", data = payload)

#crawl
if (sys.argv[1] == "crawl"):
    file_all = open("all_articles.txt", "w", encoding="utf-8")
    file_popular = open("all_popular.txt", "w", encoding="utf-8")

    #2748~3143
    for i in range(2748, 3144):
        #防止被鎖IP
        time.sleep(0.01)
        #2019的頁數選擇
        url = "https://www.ptt.cc/bbs/Beauty/index" + str(i) + ".html"
        res = rs.get(url)
        content = res.text
        soup = BeautifulSoup(content, "html.parser")
        #print(soup.text)
        title_list = soup.select("div.r-ent")
        #print(title_list)
        plain = "https://www.ptt.cc"

        for item in title_list:
            if (item.select_one("div.title").select_one("a") == None):
                continue

            #找日期
            item_date = item.select_one("div.date").text
            if (i == 2748 and item_date[0 : item_date.find("/")] == "12"):
                continue
            elif (i == 3143 and item_date[1 : item_date.find("/")] == "1"):
                continue
            else:
                if (item_date[0] == " "):
                    item_date = item_date[1 : item_date.find("/")] + item_date[item_date.find("/")+1 : ]
                else:
                    item_date = item_date[0 : item_date.find("/")] + item_date[item_date.find("/")+1 : ]
            #print(item_date)

            #找標題
            item_title = item.select_one("div.title").select_one("a").text
            #print(item_title)

            #找網址
            item_href = item.select_one("div.title").select_one("a").get("href")
            item_href = plain + item_href
            #print(item_href)

            #檔案內容格式
            result = item_date + "," + item_title + "," + item_href

            #判斷是否爆文
            if (item.select_one("div.nrec").text == "爆"):
                #print(result)
                file_popular.write(result + "\n")

            #所有2019文章(2748~3143)
            if item_title.find("[公告]") == -1:
                #print(result)
                file_all.write(result + "\n")        
    file_all.close()
    file_popular.close()

#push
elif (sys.argv[1] == "push"):
    start_date, end_date = sys.argv[2], sys.argv[3]
    file_all = open("all_articles.txt", "r", encoding="utf-8")
    file_push = open("push[" + start_date + "-" + end_date + "].txt", "w", encoding="utf-8")
    article = file_all.readlines()
    #print(article)

    count_hot, count_cold = 0, 0
    like_list, boo_list = [], []
    for item in article:
        time.sleep(0.01)
        #需扣掉換行字元\n
        url = item[item.find("https") : len(item)-1]
        #時間>end_date直接跳出迴圈
        if (int(item[0 : item.find(",")]) > int(end_date)):
            break
        #時間<start_date直接下一輪迴圈
        if (int(item[0 : item.find(",")]) < int(start_date)):
            continue
        res = rs.get(url)
        content = res.text
        soup = BeautifulSoup(content, "html.parser")
        #找出每一則留言
        push_list = soup.select("div.push")
        #print(push_list)
        #確認此篇發文是否有發信站
        if(soup.text.find("※ 發信站") > 0):
            #統計留言裡是推文或噓文
            for member in push_list:
                span_list = member.select("span")
                #留言過多的例外 -> len(span_list) == 0
                if (len(span_list) == 0):
                    continue
                #print(span_list)

                #推文or噓文
                if (span_list[0].text == "推 "):
                    count_hot += 1
                    #空list
                    if (len(like_list) == 0):
                        like_list.append([span_list[1].text, 1])
                    #非空list
                    else:
                        for i in range(len(like_list)):
                            #此人之前出現過
                            if (span_list[1].text in like_list[i]):
                                like_list[i][1] += 1
                                break
                            #此人之前未出現過
                            if (i == len(like_list)-1):
                                like_list.append([span_list[1].text, 1])
                if (span_list[0].text == "噓 "):
                    count_cold += 1
                    #空list
                    if (len(boo_list) == 0):
                        boo_list.append([span_list[1].text, 1])
                    #非空list
                    else:
                        for i in range(len(boo_list)):
                            #此人之前出現過
                            if (span_list[1].text in boo_list[i]):
                                boo_list[i][1] += 1
                                break
                            #此人之前未出現過
                            if (i == len(boo_list)-1):
                                boo_list.append([span_list[1].text, 1])
    '''                        
    like_count = 0
    boo_count = 0
    for i in range(len(like_list)):
        like_count += like_list[i][1]
    for i in range(len(boo_list)):
        boo_count += boo_list[i][1]
    print(like_count)
    print(boo_count)'''

    like_list.sort(key = lambda score: score[0])
    like_list.sort(key = lambda score: score[1], reverse = True)
    boo_list.sort(key = lambda score: score[0])
    boo_list.sort(key = lambda score: score[1], reverse = True)

    '''
    print("all like: " + str(count_hot))
    print("all boo: " + str(count_cold))
    print(like_list)
    print(boo_list)'''

    #輸出資料到file_push.txt
    file_push.write("all like: " + str(count_hot) + "\n" + "all boo: " + str(count_cold) + "\n")
    for i in range(10):
        file_push.write("like #" + str(i+1) + ": " + like_list[i][0] + " " + str(like_list[i][1]) + "\n")
    for i in range(10):
        file_push.write("boo #" + str(i+1) + ": " + boo_list[i][0] + " " + str(boo_list[i][1]) + "\n")    
        
    file_all.close()
    file_push.close()

#popular
elif (sys.argv[1] == "popular"):
    start_date, end_date = sys.argv[2], sys.argv[3]
    file_popular = open("all_popular.txt", "r", encoding="utf-8")
    file_image = open("popular[" + start_date + "-" + end_date + "].txt", "w", encoding="utf-8")
    article = file_popular.readlines()
    #print(article)

    #從熱門文章中找圖片
    popular_count = 0
    output_list = []
    for item in article:
        time.sleep(0.01)
        #需扣掉換行字元\n
        url = item[item.find("https") : len(item)-1]
        #時間>end_date直接跳出迴圈
        if (int(item[0 : item.find(",")]) > int(end_date)):
            break
        #時間<start_date直接下一輪迴圈
        if (int(item[0 : item.find(",")]) < int(start_date)):
            continue
        popular_count += 1
            
        res = rs.get(url)
        content = res.text
        soup = BeautifulSoup(content, "html.parser")
        href_list = soup.select("a")

        #確認此篇發文是否有發信站
        if(soup.text.find("※ 發信站") > 0):
        #確認圖片url是否符合格式    
            for item in href_list:
                image_url = item.get("href")
                if (image_url[-3:].lower() == "jpg" or image_url[-4:].lower() == "jpeg" or image_url[-3:].lower() == "png" or image_url[-3:].lower() == "gif"):
                    output_list.append(image_url)    
            #print(popular_count)
        
    #輸出至檔案
    file_image.write("number of popular articles: " + str(popular_count) + "\n")
    for item in output_list:
        file_image.write(item + "\n")
            
    file_popular.close()
    file_image.close()

#keyword
else:
    keyword = sys.argv[2]
    start_date, end_date = sys.argv[3], sys.argv[4]
    file_all = open("all_articles.txt", "r", encoding="utf-8")
    file_image = open("keyword" + "(" +  keyword + ")" + "[" + start_date + "-" + end_date + "].txt", "w", encoding="utf-8")
    article = file_all.readlines()

    output_list = []
    for item in article:
        time.sleep(0.01)
        #需扣掉換行字元\n
        url = item[item.find("https") : len(item)-1]
        #時間>end_date直接跳出迴圈
        if (int(item[0 : item.find(",")]) > int(end_date)):
            break
        #時間<start_date直接下一輪迴圈
        if (int(item[0 : item.find(",")]) < int(start_date)):
            continue
        
        res = rs.get(url)
        content = res.text
        soup = BeautifulSoup(content, "html.parser")
        href_list = soup.select("a")
        article = soup.text

        #確認是否符合發信帖格式
        if(article.find("※ 發信站") > 0):
            article = article[article.find("作者") : article.find("※ 發信站")]
            #確認是否有keyword
            if (article.find(keyword) > 0):
                #image_count = 0
                #找圖片url
                for item in href_list:
                    image_url = item.get("href")
                    if (image_url[-3:].lower() == "jpg" or image_url[-4:].lower() == "jpeg" or image_url[-3:].lower() == "png" or image_url[-3:].lower() == "gif"):
                        #image_count += 1
                        output_list.append(image_url)
                #print(image_count)

    for item in output_list:
        file_image.write(item + "\n")
        
    file_all.close()
    file_image.close()

