import re


sample = '☺😃Когда батя берёт дело в свои руки\n\n[https://vk.com/wall-132265_1860273|Остальное в СмешномВидео.]\n\n#УраПерерывчик'

sample = re.sub(r'\n+.+$', '', sample, 4, re.M)

print('pass')
