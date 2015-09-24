import re

class Virus():
	def __init__(self, s):
		self.strain =s
		self.breakdown_strain_name(self.strain)

	def breakdown_strain_name(self,s):
		''' Parse strain names'''
		d_prov			=province_dict()
		d_loc           =location_std()
		d_host,d_family	=host_dict()
		s_list			=s.strip().split('/')
		if len(s_list) == 4 and s_list[1].lower() != "chicken":
			self.location   =d_loc.get(s_list[1], s_list[1].title())
			self.province	=d_prov[s_list[1]]
			self.host		='Human'
			self.opt_id		='/'.join(s_list[2:-1])
		else:
			self.location   =d_loc.get(s_list[2], s_list[2].title())
			self.province	=d_prov[s_list[2]]
			self.host		=d_host[s_list[1]]
			self.opt_id		='/'.join(s_list[3:-1])

	@property
	def year(self):
		y	=self.strain.rsplit('/',1)[-1].strip()
		# parse year info
		if y.isdigit():
			return Virus.reformat_year( y )
		elif y in ["China", "Hubei"]: # two special strains with names ended w/o year
			return None
		else:
			year_pat	=r'(?<!\d)([1|2][9|0]\d{2})($|/|-|\()'
			return int(re.search(year_pat, self.strain).group(1))

	@staticmethod	
	def reformat_year(y):
		'''
		convert year to standard format 19xx / 20xx
		'''
		if len(y) == 4:
			yy=y
		else:
			assert len(y) == 2, "The year format is: %s"%y
			if int(y) > 20:
				yy='19'+y
			else:
				yy='20'+y
		return int(yy)

	@property
	def std_name(self):
		return 'A/%s/%s/%s/%s'%(self.host, self.location, self.opt_id, self.year)
	
	@property
	def name(self):
		'''
		Will and only will change year format to four digits
		'''
		l   =self.strain.rsplit('/',1)
		if l[-1].isdigit():
			return '%s/%d'%(l[0],Virus.reformat_year( l[-1] ))
		else:
			return self.strain

##------------ Manual curated dictionaries ----------##
def location_std():
    s='''\
    HK:Hong Kong
    Hong_Kong:Hong Kong
    HongKong:Hong Kong
    YN:Yunnan'''
    return {l.strip().split(':')[0]:l.strip().split(':')[1]
            for l in s.split('\n')}

def province_dict():
    '''
    
    This dictionary is manually curated for virus strain name
    city:province

    Dictionary updates:
    ==== SW 6/16/2014 ====
    corrected Yunan:Yunan to Yunan:Yunnan
              YN:Yunan to YN:Yunnan
    ==== SW 07/22/2014 ====
    Added the following when analyze H5N1 data 
    (did not finish and did not confirm with Juan)
    Guiyang:Guizhou
    Huadong:Fujian
    ST:Guangdong

    '''
    s='''\
    Anhui:Anhui
    Anhui-Chuzhou:Anhui
    AnhuiChuzhou:Anhui
    Banna:Yunnan
    Baoshan:Yunnan
    Beijing:Beijing
    Changsha:Hunan
    Chang Sha:Hunan
    Chang_Sha:Hunan
    China:China
    Chongqing:Chongqing
    Dawang:Guangdong
    Dehong:Yunnan
    Dongting:Jiangxi
    Eastern China:China
    Eastern_China:China
    Fujian:Fujian
    Gangxi:Jiangxi
    Gansu:Gansu
    GuanDong:Guangdong
    Guangdong:Guangdong
    Guangdongg:Guangdong
    Guangxi:Guangxi
    GuangXi:Guangxi
    Guangzhou:Guangdong
    Guizhou:Guizhou
    Guiyang:Guizhou
    Hainan:Hainan
    Hangzhou:Zhejiang
    Hebei:Hebei
    Heibei:Hebei
    Heilongjiang:Heilongjiang
    Henan:Henan
    HK:Hong Kong
    Hong Kong:Hong Kong
    Hong_Kong:Hong Kong
    Honghe:Yunnan
    HongKong:Hong Kong
    Huadong:Fujian
    Huangdong:Henan
    Hubei:Hubei
    Huizhou:Guangdong
    Hunan:Hunan
    Huzhou:Zhejiang
    Jiande:Zhejiang
    jiangsu:Jiangsu
    Jiangsu:Jiangsu
    Jiangxi:Jiangxi
    Jiawang:Jiangsu
    JiIangsu:Jiangsu
    Jilin:Jilin
    Kaifeng:Henan
    Kunming:Yunnan
    Liaoning:Liaoning
    Lijiang:Yunnan
    Lincang:Yunnan
    Mudanjiang:Heilongjiang
    Nanchang:Jiangxi
    Nanjing:Jiangsu
    Nantong:Jiangsu
    Neimeng:Neimenggu
    Neimonggu:Neimonggu
    Ningxia:Ningxia
    Puer:Yunnan
    Qianzhou:Jiangsu
    Qingdao:Shandong
    Qixian:Henan
    Rizhao:Shandong
    Sandong:Shandong
    Shaanxi:Shaanxi
    Shandong:Shandong
    ShanDong:Shandong
    Shangdong:Shandong
    shanghai:Shanghai
    Shanghai:Shanghai
    Shangqiu:Henan
    Shantou:Guangdong
    ST:Guangdong
    ShanXi:Shanxi
    Shanxi:Shanxi
    Shaoguan:Guangdong
    Shenyang:Liaoning
    Shenzhen:Shenzhen
    Shijiazhuang:Hebei
    Shuanggou:Jiangsu
    Sichuan:Sichuan
    Suzhou:Jiangsu
    Taixing:Jiangsu
    Taizhou:Zhejiang
    Tianjin:Tianjin
    Tianjing:Tianjin
    Tibet:Tibet
    Tongshan:Jiangsu
    Wangcheng:Changsha
    Wenshan:Yunnan
    Wenzhou:Zhejiang
    Wisconsin:Wisconsin
    Wujin:Jiangsu
    Wuxi:Jiangsu
    Xianghai:Jilin
    Xiangshui:Jiangsu
    Xigou:Jiangsu
    Xinjiang:Xinjiang
    Xuchang:Sichuan
    Xuzhou:Jiangsu
    Yangzhou:Jiangsu
    Yongcheng:Jiangsu
    YN:Yunnan
    Yunan:Yunnan
    Yunnan:Yunnan
    Yunnanbn:Yunnan
    Yunnandh:Yunnan
    Yunnanws:Yunnan
    Zhejiang:Zhejiang
    Zhenjiang:Jiangsu
    Zhuhai:Guangzhou
    Zibo:Shandong'''
    return {l.strip().split(':')[0]:l.strip().split(':')[1] 
            for l in s.split('\n')}
def host_dict():
    '''
    
    Manually curiated dictionary in the format:
    host name, standardized host name, group name
    
    ==== SW 07/22/2014 ====
    Added the following when analyze H5N1 data
    (did not finish and did not confirm with Juan)
    domestic green-winged teal,Domestic Green-winged Teal,wild bird
    shrike,Shrike,wild bird
    '''
    s='''\
    avian,Avian,Avian
    baikal teal,Baikal Teal,wild bird
    baikal_teal,Baikal Teal,wild bird
    bird,Bird,wild bird
    black_billed_magpie,Black Billed Magpie,wild bird
    black-billed magpie,Black Billed Magpie,wild bird
    black-billed_magpie,Black Billed Magpie,wild bird
    brambling,Brambling,wild bird
    canine,Canine,mammalian
    chicken,Chicken,poultry
    Chicken,Chicken,poultry
    ChiCken,Chicken,poultry
    chukkar,Chukkar,wild bird
    Ck,Chicken,poultry
    common teal,Common Teal,wild bird
    Common Teal,Common Teal,wild bird
    common_teal,Common Teal,wild bird
    domestic green-winged teal,Domestic Green-winged Teal,wild bird
    duck,Duck,poultry
    Duck,Duck,poultry
    egret,Egret,wild bird
    Enviroment,Environment,Environment
    environment,Environment,Environment
    Environment,Environment,Environment
    equine,Equine,mammalian
    feces,Feces,Environment
    goose,Goose,poultry
    Gf,Guinea Fowl,wild bird
    guinea fowl,Guinea Fowl,wild bird
    Guinea fowl,Guinea Fowl,wild bird
    guinea_fowl,Guinea Fowl,wild bird
    Guinea_fowl,Guinea Fowl,wild bird
    guineafowl,Guinea Fowl,wild bird
    GuineaFowl,Guinea Fowl,wild bird
    homing pigeon,Homing Pigeon,poultry
    homing_pigeon,Homing Pigeon,poultry
    Human,Human,Human
    mallard,Mallard,wild bird
    Mallard,Mallard,wild bird
    Muscovy duck,Muscovy Duck,poultry
    Muscovy_duck,Muscovy Duck,poultry
    partridge,Partridge,poultry
    Ph,Pheasant,poultry
    pheasant,Pheasant,poultry
    Pheasant,Pheasant,poultry
    pigeon,Pigeon,poultry
    Pigeon,Pigeon,poultry
    quail,Quail,poultry
    Quail,Quail,poultry
    SCk,Silkie Chicken,poultry
    shrike,Shrike,wild bird
    silkie chicken,Silkie Chicken,poultry
    Silkie Chicken,Silkie Chicken,poultry
    silkie_chicken,Silkie Chicken,poultry
    Silkie_Chicken,Silkie Chicken,poultry
    silky chicken,Silkie Chicken,poultry
    Silky Chicken,Silkie Chicken,poultry
    silky_chicken,Silkie Chicken,poultry
    Silky_Chicken,Silkie Chicken,poultry
    sparrow,Sparrow,poultry
    spot_billed_duck,Spot Billed Duck,wild bird
    spot-billed duck,Spot Billed Duck,wild bird
    spot-billed_duck,Spot Billed Duck,wild bird
    Sw,Swine,mammalian
    swine,Swine,mammalian
    Swine,Swine,mammalian
    tree sparrow,Tree Sparrow,wild bird
    tree_sparrow,Tree Sparrow,wild bird
    turkey,Turkey,poultry
    wild pigeon,Wild Pigeon,wild bird
    wild duck,Wild Duck,wild bird
    Wild Duck,Wild Duck,wild bird
    wild waterfowl,Wild Waterfowl,wild bird
    Wild_Duck,Wild Duck,wild bird
    wild_duck,Wild Duck,wild bird
    wild_pigeon,Wild Pigeon,wild bird
    wild_waterfowl,Wild Waterfowl,wild bird'''
    host_dict ={l.strip().split(',')[0]:l.strip().split(',')[1] 
                    for l in s.split('\n')}
    class_dict ={l.strip().split(',')[0]:l.strip().split(',')[2] 
                    for l in s.split('\n')}
    return host_dict, class_dict

