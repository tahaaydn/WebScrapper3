#%%
import requests
import xlsxwriter
import os
from bs4 import BeautifulSoup

HEADERS = ({
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept-Language': 'en-US, en;q=0.5'
})

payload = {'email': 'placeholder@mail.com', 'pass': 'password'}

sitemapProductList = [
    "placeholder.com/xml/sitemap_product_1.xml",
    "placeholder.com/xml/sitemap_product_2.xml",
    "placeholder.com/xml/sitemap_product_3.xml",
    "placeholder.com/xml/sitemap_product_4.xml",
    "placeholder.com/xml/sitemap_product_5.xml"
]

if __name__ == "__main__":
    download_images = "y" if input("Download images? [y/n]\n").lower() == "y" else "n"
    
    with requests.Session() as session:
        post = session.post("placeholder.com/login", data=payload, headers=HEADERS)
        product_info = []
        pageCount = 0
        
        for list in sitemapProductList:
            page = requests.get(list, headers=HEADERS)
            soup = BeautifulSoup(page.content, 'html.parser')
            products = [link.string for link in soup.find_all('loc')]
            
            pageCount += 1
            progress = 0            

            for link in products:
                if (product_page := session.get(link, headers=HEADERS)).status_code == 200:
                    soup = BeautifulSoup(product_page.content, 'html.parser')
                    
                    try:
                        productName = str([a.text.strip() for a in soup.select("#urun_adi > td > h1")][0])
                    except:
                        productName = ''
                        pass
                    
                    try:
                        productBrand = str([a.text.strip() for a in soup.select("#etiketler_tip_3 > td > a")]).replace('[', '').replace(']', '').replace("'", '')
                    except:
                        productBrand = ''
                        pass
                        
                    try:
                        productStokKodu = str([a.text.strip() for a in soup.select("#stok_kodu > td.col3")]).replace('[', '').replace(']', '').replace("'", '')
                    except:
                        productStokKodu = ''
                        pass
                    try:
                        productPrice = float([a.text.strip() for a in soup.select(".row18")][0].replace('TL','').replace('.', '').replace(',','.').strip())
                    except:
                        productPrice = 0
                        pass
                    
                    try:
                        productCategory = str([a.text.strip() for a in soup.select("#etiketler_tip_2 > td.col3 > a")][0])
                    except:
                        productCategory = ''
                        pass
                    
                    try:
                        productStatus = "+" if str(soup.select("#sepet_butonlari > div._floatLeft.mR10._positionRelative > a > img")).find("globalRemindmeButton") == -1 else "-"
                    except:
                        productStatus = '?'
                        pass
                    
                    if download_images == "y":
                        try:
                            productImageList = soup.find_all("div", {"class": "thumbsImage _clearfix"})[0].find_all("img")
                        except:
                            productImageList = ''
                            pass
                        
                        try:
                            if productImageList != '':
                                for i in range(len(productImageList)):
                                    response = requests.get("http:" + productImageList[i]['src'])
                                    if response.status_code == 200:
                                        with open(productStokKodu + "_" + str(i) + ".png", "wb") as f:
                                            f.write(response.content)
                                    else:
                                        pass
                            else:
                                pass
                        except:
                            pass
                    else:
                        pass
                    
                    product_info.append([productStokKodu, productName, productBrand, productPrice, productCategory, productStatus])
                    progress += 1
                    print('Progess: %d / %d, Page %d / %d' % (progress, len(products), pageCount, len(sitemapProductList)))
                else:
                    print("Connection Error...")
                    break
            
    with xlsxwriter.Workbook('data.xlsx') as workbook:
        worksheet = workbook.add_worksheet()
        headers = [['Ürün Stok Kodu', 'Ürün Adı', 'Ürün Markası', 'Ürün Fiyatı', 'Ürün Kategorisi', 'Ürün Stok Durumu']]
        for row_num, data in enumerate(headers + product_info):
            worksheet.write_row(row_num, 0, data)
    
    print("Scrapping succesfully finished.")
# %%
