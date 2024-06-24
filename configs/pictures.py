import numpy as np

days = np.array(['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота'])

path_to_pics = np.array(['pics/pn.png',
				'pics/vt.png',
				'pics/sr.png',
				'pics/ch.png',
				'pics/pt.png',
				'pics/sb.png'])

days_p_dict = dict(zip(days,path_to_pics))