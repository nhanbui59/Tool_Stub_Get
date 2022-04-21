# -*- coding: utf-8 -*- 

class Convert:
	def __init__(self,string):
		self.string = string

	@staticmethod
	def dictionay_hafttofull():
		Hafl = ("ｧ", "ｱ", "ｨ", "ｲ", "ｩ", "ｳ", "ｪ", "ｴ", "ｫ", "ｵ", "ｶ", "ｶﾞ", "ｷ", "ｷﾞ", "ｸ", "ｸﾞ", "ｹ", "ｹﾞ", "ｺ", "ｺﾞ", "ｻ", "ｻﾞ", "ｼ", "ｼﾞ", "ｽ", "ｽﾞ", "ｾ", "ｾﾞ", "ｿ", "ｿﾞ", "ﾀ", "ﾀﾞ", "ﾁ", "ﾁﾞ", "ｯ", "ﾂ", "ﾂﾞ", "ﾃ", "ﾃﾞ", "ﾄ", "ﾄﾞ", "ﾅ", "ﾆ", "ﾇ", "ﾈ", "ﾉ", "ﾊ", "ﾊﾞ", "ﾊﾟ", "ﾋ", "ﾋﾞ", "ﾋﾟ", "ﾌ", "ﾌﾞ", "ﾌﾟ", "ﾍ", "ﾍﾞ", "ﾍﾟ", "ﾎ", "ﾎﾞ", "ﾎﾟ", "ﾏ", "ﾐ", "ﾑ", "ﾒ", "ﾓ", "ｬ", "ﾔ", "ｭ", "ﾕ", "ｮ", "ﾖ", "ﾗ", "ﾘ", "ﾙ", "ﾚ", "ﾛ", "ヮ", "ﾜ", "ｦ", "ﾝ", "ｳﾞ", "･", "ｰ", "､")
		full = ("ァ", "ア", "ィ", "イ", "ゥ", "ウ", "ェ", "エ", "ォ", "オ", "カ", "ガ", "キ", "ギ", "ク", "グ", "ケ", "ゲ", "コ", "ゴ", "サ", "ザ", "シ", "ジ", "ス", "ズ", "セ", "ゼ", "ソ", "ゾ", "タ", "ダ", "チ", "ヂ", "ッ", "ツ", "ヅ", "テ", "デ", "ト", "ド", "ナ", "ニ", "ヌ", "ネ", "ノ", "ハ", "バ", "パ", "ヒ", "ビ", "ピ", "フ", "ブ", "プ", "ヘ", "ベ", "ペ", "ホ", "ボ", "ポ", "マ", "ミ", "ム", "メ", "モ", "ャ", "ヤ", "ュ", "ユ", "ョ", "ヨ", "ラ", "リ", "ル", "レ", "ロ", "ヮ", "ワ", "ヲ", "ン", "ヴ", "・", "ー", "ヽ")
		dictionary_haft_full = {}
		for i_count in range(len(Hafl)):
			dictionary_haft_full[Hafl[i_count]] = full[i_count]
		return dictionary_haft_full	

	def convert_haft2full_katakana(self):
		string_old = self.string
		dictionary_haft_full = Convert.dictionay_hafttofull()
		string_list = list(string_old)
		i_count_char = 0
		max_char = len(string_list)
		while i_count_char < max_char:
			try:
				if string_list[i_count_char]+string_list[i_count_char+1] in dictionary_haft_full:
					string_list[i_count_char] = dictionary_haft_full[string_list[i_count_char]+string_list[i_count_char+1]]
					string_list[i_count_char+1] = ""
					i_count_char += 1
				elif string_list[i_count_char] in dictionary_haft_full:
					string_list[i_count_char] = dictionary_haft_full[string_list[i_count_char]]
			except:
				if string_list[i_count_char] in dictionary_haft_full:
					string_list[i_count_char] = dictionary_haft_full[string_list[i_count_char]]
			i_count_char += 1
		return "".join(string_list)