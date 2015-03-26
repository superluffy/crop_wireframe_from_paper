#coding:utf-8
import cv2
import numpy as np

from os import listdir
files = listdir('input/')

DEBUG_PROCESS = 0

def sort_corner(box):
	center_x = 0.0
	center_y = 0.0
	for point in box:
		center_x += point[0]
		center_y += point[1]
	center_x = center_x / 4.0
	center_y = center_y / 4.0

	p_left_lower = None
	p_right_lower = None
	p_left_upper = None
	p_right_upper = None

	for point in box:
		x = point[0]
		y = point[1]
		if x > center_x and y > center_y:
			p_right_upper = point
		elif x < center_x and y > center_y:
			p_left_upper = point
		elif x > center_x and y < center_y:
			p_right_lower = point
		elif x < center_x and y < center_y:
			p_left_lower = point
	return (p_left_lower,
			p_right_lower,
			p_left_upper,
			p_right_upper)

for f in files:
	# if DEBUG_PROCESS == 1:
	# 	f = 'IMG_1466.jpg'
	fname = f.split('.')[0]
	filename = "input/" + f 
	im_original = cv2.imread(filename)
	im = cv2.imread(filename)
	gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
	cv2.imwrite("b.jpg", gray)
	blur = cv2.GaussianBlur(gray,(5,5),1000)
	cv2.imwrite("c_gaussian.jpg", blur)

	#定义结构元素
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(50, 50))  

	#闭运算  
	closed = cv2.morphologyEx(blur, cv2.MORPH_CLOSE, kernel)  
	cv2.imwrite("CLOSED.jpg", closed)

	# for i in range(1,20):
	# 	thresh_val = 80 + i*10
	# 	flag, thresh = cv2.threshold(blur, thresh_val, 255, cv2.THRESH_BINARY)
	# 	cv2.imwrite("d_thresh"+str(thresh_val)+".jpg", thresh)


	ITEM_PER_PAGE = 3
	for i in range(1,2):
		thresh_val = 80 + i*10
		# flag, thresh = cv2.threshold(blur, thresh_val, 255, cv2.THRESH_BINARY)
		thresh = cv2.adaptiveThreshold(closed,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,51,2) 
		cv2.imwrite("d_thresh"+str(thresh_val)+".jpg", thresh)
		numcards = 1
		contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		contours = sorted(contours, key=cv2.contourArea,reverse=True)
		
		if DEBUG_PROCESS == 1:
			print contours[1:2]
			print '---len---'
			print len(contours[1:2])
			print '========='
			cv2.drawContours(im,contours[1:2],-1,(0,255,0),3)	
			cv2.imwrite("output/"+fname+".jpg", im)
			cv2.imwrite(fname+".jpg", im)


		#for fucking test :
		# for i in range(0,50):
		# 	im = cv2.imread(filename)
		# 	cv2.drawContours(im,contours[i:i+1],-1,(0,255,0),3)	
		# 	cv2.imwrite("output/"+fname+"_"+ str(i) + ".jpg", im)
		# 	cv2.imwrite(fname+".jpg", im)

		#end for fucking test

		###find the right contours

		print '-------------------'
		succ = -1
		succ_page = 1
		for i in range(1,50):

			peri = cv2.arcLength(contours[i],True)
			approx = cv2.approxPolyDP(contours[i],0.02*peri,True)
			rect = cv2.minAreaRect(contours[i])
			r = cv2.cv.BoxPoints(rect)
			
			# print r

			min_x = 9999999
			max_x = -1
			min_y = 9999999
			max_y = -1

			for item in approx:
				x = item[0][0]
				y = item[0][1]
				if x < min_x:
					min_x = x
				if x > max_x:
					max_x = x
				if y < min_y:
					min_y = y
				if y > max_y:
					max_y = y
			length = max_x - min_x
			height = max_y - min_y
			# if DEBUG_PROCESS == 1:
			# 	print "FUCKME length" + str(length) 
			# 	print "FUCKME height" + str(height)
			# inner
			# 800 X 1400
			# 550 X 1050		

			# outer
			# 900 * 1800
			# 700 * 1400	
			
			if length > 600 and length < 1000 and height > 1400 and height < 1800:
				succ = 1
				print 'HIT'
				outfname = "output_final/"+fname+ "_" + str(succ_page)+".jpg"
				print outfname

				#for fucking test :
				if DEBUG_PROCESS == 1:
					imtest = cv2.imread(filename)
					cv2.drawContours(imtest,contours[i:i+1],-1,(0,255,0),3)	
					cv2.imwrite("output/"+fname+"_"+ str(i) + ".jpg", imtest)
					cv2.imwrite(fname+".jpg", imtest)

				#end for fucking test
				
				for item in approx:
					print item
					print '---'

				rect = cv2.minAreaRect(contours[i])
				box = cv2.cv.BoxPoints(rect)

				box = sort_corner(box)
				fbox = np.float32(box)
				ibox = np.int0(box)
				
				if DEBUG_PROCESS == 1:
					
					imtest = cv2.imread(filename)		
					cv2.drawContours(imtest,[ibox],0,(0,0,255),2)
					cv2.imwrite("MIN_AREA_RECT.jpg",imtest)

				h = np.array([ [0,0],[820,0],[0,1700],[820,1700] ],np.float32)


				if DEBUG_PROCESS == 1:
					print '==================box==================='
					print box
					print fbox
					print ibox
					print type(fbox)
					print len(box)
					print '==================h==================='
					print h
					print len(h)
					print '========================================'


				transform = cv2.getPerspectiveTransform(fbox,h)
				warp = cv2.warpPerspective(im_original,transform,(820,1700))
				if DEBUG_PROCESS == 1:
					# output corrected image
					cv2.imwrite("IMAGE_WRAP.jpg", warp)
					cv2.imwrite("IMAGE_WRAP_NONE.jpg", im_original[min_y:max_y, min_x:max_x])

				# output original image cut
				cv2.imwrite(outfname, warp)
				succ_page = succ_page + 1
				# break

		if succ == -1:
			cv2.imwrite("failed/"+ fname + ".jpg", im_original)
		else:
			cv2.imwrite("page_%d/" %(succ_page -1) + fname + ".jpg", im_original)
		contours_index = i	
		print '-------succ_page---------' + str(succ_page) + '---------------'

	if DEBUG_PROCESS == 1:
		break
		###end find the right contours
