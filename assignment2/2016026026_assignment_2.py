# 인공지능 assignment2
# 2016026026 컴퓨터전공 최솔비

from konlpy.tag import Mecab
import sys
import os
import string
import math

pos_cnt = 0
neg_cnt = 0
pos_word_cnt = 0
neg_word_cnt = 0
pos_words = {}
neg_words = {}


# 각 단어의 긍정빈도 혹은 부정빈도(확률)를 로그를 취한 값으로 리턴합니다. 
def caculate_prob(bool, word):
	global pos_word_cnt, neg_word_cnt, pos_words, neg_words

	if bool == 1:
		total = pos_word_cnt
		dic = pos_words

	else:
		total = neg_word_cnt
		dic = neg_words

	# test case 에서 처음 등장한 단어의 확률을 계산할때 0을 곱하게 되는 것을 방지하기 위해(혹은 로그0 계산)
	# 적당히 작은 상수 k를 분자와 분모에 더해줍니다. 
	k = 0.5

	if dic.get(word) == None:
		v = 0
	else:
		v = dic[word]


	return ( math.log(k + float(v)) - math.log(2.0 * k + float(total)) )


def dic_input(dic, word):
	if dic.get(word) == None:
		dic[word] = 1

	else:
		dic[word] += 1


#train 파일을 읽어 단어의 개수를 세어 dictionary형태로 저장합니다. 
def read_train_file(path):

	global pos_word_cnt, neg_word_cnt, pos_words, neg_words, pos_cnt, neg_cnt

	mecab = Mecab()
	f = open(os.path.expanduser(path))
	line = f.readline()

	number = 0

	while True :

		number += 1
		if number % 1000 == 0:
			print("line: ", number)

		line = f.readline()
		if not line:
			break
		line = line.rstrip('\n')

		# lineSplited[0]에는 id, [1]에는 text, [2]에는 긍정('1') 또는 부정('0')
		lineSplited = line.split('\t')

		# 형태소 단위로 분석합니다.
		analyzedLine = mecab.morphs(lineSplited[1])
		# print(analyzedLine)

		# 긍정적인 comment 일 경우, 긍정 딕셔너리에 input 하여 word counting 합니다. 
		if lineSplited[2] == '1':
			pos_cnt += 1
			for word in analyzedLine:
				pos_word_cnt += 1
				dic_input(pos_words, word)

		# 부정적인 comment 일 경우, 부정 딕셔너리에 input 하여 word counting 합니다.
		elif lineSplited[2] == '0':
			neg_cnt += 1
			for word in analyzedLine:
				neg_word_cnt += 1
				dic_input(neg_words, word)

		else:
			print("parse error")
			break


	print("POS:", pos_word_cnt)
	#print(pos_words)
	print("NEG:", neg_word_cnt)
	#print(neg_words)

	f.close()

# 분석한 train file 의 결과를 텍스트 파일로 저장합니다. 
def save_train_result(path):

	global pos_word_cnt, neg_word_cnt, pos_words, neg_words, pos_cnt, neg_cnt

	f = open(os.path.expanduser(path), 'w')

	f.write(str(pos_cnt)+" "+str(neg_cnt)+"\n")
	f.write(str(pos_word_cnt)+" "+str(neg_word_cnt)+"\n")
	for word in pos_words.keys():
		f.write(word+" "+str(pos_words[word])+"\t")
	f.write("\n")
	for word in neg_words.keys():
		f.write(word+" "+str(neg_words[word])+"\t")

	f.close()

# 텍스트 파일로 저장된 train 결과를 읽어 메모리에 올립니다. 
def load_train_result(path):

	global pos_word_cnt, neg_word_cnt, pos_words, neg_words, pos_cnt, neg_cnt

	f = open(os.path.expanduser(path), 'r')

	line = f.readline()
	line = line.rstrip('\n')
	lineSplited = line.split(" ")
	pos_cnt = int(lineSplited[0])
	neg_cnt = int(lineSplited[1])

	line = f.readline()
	line = line.rstrip('\n')
	lineSplited = line.split(" ")
	pos_word_cnt = int(lineSplited[0])
	neg_word_cnt = int(lineSplited[1])

	line = f.readline()
	line = line.rstrip('\t\n')
	lineSplited = line.split('\t')
	for string in lineSplited:
		oneWord = string.split(" ")
		pos_words[oneWord[0]] = int(oneWord[1])

	line = f.readline()
	line = line.rstrip('\t\n')
	lineSplited = line.split('\t')
	for string in lineSplited:
		oneWord = string.split(" ")
		neg_words[oneWord[0]] = int(oneWord[1])

	f.close()

	print(pos_cnt, neg_cnt)
	print(pos_word_cnt, neg_word_cnt)
	# print(pos_words)
	# print(neg_words)


def test_valid_file(path):

	global pos_word_cnt, neg_word_cnt, pos_words, neg_words, pos_cnt, neg_cnt

	true_pos = 0
	true_neg = 0
	false_pos = 0
	false_neg = 0

	mecab = Mecab()
	f = open(os.path.expanduser(path))
	line = f.readline()

	while True :

		line = f.readline()
		if not line:
			break
		line = line.rstrip('\n')

		# lineSplited[0]에는 id, [1]에는 text
		lineSplited = line.split('\t')

		# 형태소 단위로 분석합니다.
		analyzedLine = mecab.morphs(lineSplited[1])
		# print(analyzedLine)

		#각각의 word에 대해 긍정과 부정의 확률을 계산합니다.
		log_pos_prob = math.log(pos_cnt / (pos_cnt + neg_cnt) )
		log_neg_prob = math.log(neg_cnt / (pos_cnt + neg_cnt) )
		for word in analyzedLine:
			log_pos_prob += caculate_prob(1, word)
			log_neg_prob += caculate_prob(0, word)

		# print("POS:", log_pos_prob)
		# print("NEG:", log_neg_prob)

		if log_pos_prob >= log_neg_prob:
			if lineSplited[2] == '1':
				true_pos += 1
			else:
				false_pos += 1
				#print(lineSplited[1], lineSplited[2])

		else:
			if lineSplited[2] == '0':
				true_neg += 1
			else:
				false_neg += 1
				#print(lineSplited[1], lineSplited[2])

	f.close()
	print("true positive: ", true_pos)
	print("true negative: ", true_neg)
	print("false positive: ", false_pos)
	print("false negative: ", false_neg)


def classify(origin, result):

	global pos_word_cnt, neg_word_cnt, pos_words, neg_words, pos_cnt, neg_cnt

	fw = open(os.path.expanduser(result), 'w')

	mecab = Mecab()
	f = open(os.path.expanduser(origin),'r')
	line = f.readline()
	fw.write(line)

	while True :

		line = f.readline()
		if not line:
			break
		line = line.rstrip('\n')

		# lineSplited[0]에는 id, [1]에는 text
		lineSplited = line.split('\t')

		# 형태소 단위로 분석합니다.
		analyzedLine = mecab.morphs(lineSplited[1])
		# print(analyzedLine)

		#각각의 word에 대해 긍정과 부정의 확률을 계산합니다.
		log_pos_prob = math.log(pos_cnt / (pos_cnt + neg_cnt) )
		log_neg_prob = math.log(neg_cnt / (pos_cnt + neg_cnt) )
		for word in analyzedLine:
			log_pos_prob += caculate_prob(1, word)
			log_neg_prob += caculate_prob(0, word)

		# print("POS:", log_pos_prob)
		# print("NEG:", log_neg_prob)

		# 결과 파일에 태그를 달아 기록합니다. 
		if log_pos_prob >= log_neg_prob:
			fw.write(lineSplited[0]+'\t'+lineSplited[1]+'\t'+str(1)+'\n')

		else:
			fw.write(lineSplited[0]+'\t'+lineSplited[1]+'\t'+str(0)+'\n')
			
	f.close()
	fw.close()


def main():

	# read_train_file("./ratings_data/ratings_train.txt")
	# save_train_result("./ratings_data/trained_data_save.txt")

	load_train_result("./ratings_data/trained_data_save.txt")

	#test_valid_file("./ratings_data/ratings_valid.txt")
	classify("./ratings_data/ratings_test.txt", "./ratings_data/ratings_result.txt")



if __name__ == "__main__":
	main()
