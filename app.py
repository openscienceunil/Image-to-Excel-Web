__version__ = u'0.0.2'
__author__ = "Xavier Barros"
__maintainer__ = "Xavier Barros"
__email__ = "xavier.barros@unil.ch"


from pylab import array, imshow, show, close, gray
import pickle, sys,  os
from scipy.ndimage import measurements
import xlwt
import Tkinter  
from tkFileDialog import askopenfilename
from PIL import Image
import subprocess as sp
from flask import Flask, render_template, request, jsonify
from werkzeug import secure_filename
import json

app = Flask(__name__)

user = os.environ.get("USER")
UPLOAD_FOLDER = os.path.normpath("/Users/"+str(user)+"/Desktop/")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS 1'] = set(['xls'])


@app.route('/')
def index():
    return render_template('index.html')
	
@app.route('/table', methods=['POST'])
def make_table():
    if request.method == 'POST':
        
        img_table, img, path_name = choose_img()
        #print path_name

        if img_table == None and img == None and path_name == None :
            return render_template('error.html')
        # ceate array
        img_block_array = array(img_table)
        img_array = array(img)

        # ici choisir ce qu'on veut annalyser comme tableau (min et max pour les boite)... 
        panel_boxes = find_objects_with_size(
            img_block_array,
            min_height=40,
            min_width=100,
            max_width=600,
            max_height=600
            )
        #print len(panel_boxes), " apres selection"
          
        dico_text, nb_column, list_text = write_text_from_panels(img_array, panel_boxes)
        list_text = "__xb__".join(list_text)
        #print (list_text)
        
        
        return render_template('table.html', result = [dico_text, nb_column, len(dico_text), path_name, list_text])
             
@app.route('/test')
def test():
    list = [1,2]
    return render_template('test.html', result = list)    

@app.route('/upload', methods=['GET'])
def upload():

    ret_data = {"value": request.args.get('list_text', type=str)}
    list_text = ret_data['value'].split("__xb__")
    ret_data = {"value": request.args.get('nb_column', type=int)}
    nb_column = ret_data['value']
    ret_data = {"value": request.args.get('path_name', type=str)}
    path_name = ret_data['value']

    creer_doc_xls(list_text, nb_column, path_name)
    
    ret_data['value'] = "L'image '"+path_name+"' a ete telechargee en tableau excel sur le bureau !"
    return jsonify(ret_data)

def choose_img():
    # selectionner image
    root = Tkinter.Tk()
    filepath = askopenfilename(title="Ouvrir une image",filetypes=[("JPG","*.jpg"),("PNG","*.png"),('all files','.*')])
    path_name = os.path.basename(filepath)[:-4]
    path_end = os.path.basename(filepath)[-4:]

    root.destroy()

    # verifier que c'est un fichier image
    file_allowed = ['jpg', 'png', 'PNG', 'JPG']
    if os.path.basename(filepath)[-3:] not in file_allowed:
        return None, None, None
        

    # ouvrir l'image a traiter    
    img = Image.open(filepath)

    # purifier image et faire apparaitre les cases
    img_tableau_noir = img.point(lambda i: (i-127)*2.3).point(lambda i: 0 if i < 250 else 255)
    img_tableau_noir = purifier_col_tableau(img_tableau_noir, path_end)
    #print "colonne OK !"
    img_tableau_noir = purifier_line_tableau(img_tableau_noir, path_end)
    #print "ligne OK !"
    img_tableau_blanc = img_tableau_noir.point(lambda i: 0 if i == 255 else 255)

    #purifier image de base
    img = img.point(lambda i: (i-127)*2.3).point(lambda i: 0 if i < 50 else 255)
      
    return img_tableau_blanc, img, path_name


def purifier_col_tableau(im, path_end):

    pixels = im.load() 
    width, height = im.size

    #liste de pixel par colonne 
    col_pixels=[]
    tot_pixels_col=[]
    for x in range(width):
        for y in range(height):
            cpixel = pixels[x, y]
            col_pixels.append(cpixel)
        tot_pixels_col.append(col_pixels)
        col_pixels=[]
        
    # nettoyen les pixel noir non desire    
    l=[]
    for i in range(len(tot_pixels_col)):
        if path_end == '.png':
            pixel_noir = tot_pixels_col[i].count((0,0,0,255))
            if pixel_noir != 0:
                l.append(pixel_noir)
        elif path_end =='.jpg':
            pixel_noir = tot_pixels_col[i].count((0,0,0))
            if pixel_noir != 0:
                l.append(pixel_noir)
    moy = sum(l)/(2*len(l)) 
    
    for i in range(len(tot_pixels_col)):    
        if path_end == '.png':
            if tot_pixels_col[i].count((0,0,0,255)) < moy:
                tot_pixels_col[i] = [(255, 255, 255, 255)] * len(tot_pixels_col[i])
        elif path_end =='.jpg':
            if tot_pixels_col[i].count((0,0,0)) < moy:
                tot_pixels_col[i] = [(255, 255, 255)] * len(tot_pixels_col[i])

    #retranscrire en ligne pour retranscrir correctement
    tot_pixels=[]
    line_pixels=[]
    for i in range(len(tot_pixels_col[0])):
        for j in range(len(tot_pixels_col)):
            line_pixels.append(tot_pixels_col[j][i])
        tot_pixels+=line_pixels
        line_pixels=[]
     
    # creer la nouvelle image
    img_new= Image.new("RGB",(width, height), "white" )    
    img_new.putdata(tot_pixels)
    
    return img_new
    
    
def purifier_line_tableau(im, path_end): # non utiliser mais je le met au cas ou...

    pixels = im.load() 
    width, height = im.size

    #liste de pixel par ligne 
    col_pixels=[]
    tot_pixels=[]
    for y in range(height):
        for x in range(width):
            cpixel = pixels[x, y]
            col_pixels.append(cpixel)
        tot_pixels.append(col_pixels)
        col_pixels=[]
        
        
    # nettoyen les pixel noir non desire 
    l=[]
    for i in range(len(tot_pixels)):
        pixel_noir = tot_pixels[i].count((0,0,0))
        #print pixel_noir
        if pixel_noir != 0:
            l.append(pixel_noir)
    moy = sum(l)/(2*len(l))  
    
    for i in range(len(tot_pixels)):
        if tot_pixels[i].count((0,0,0)) < 350:
                tot_pixels[i] = [(255, 255, 255)] * len(tot_pixels[i])

            
    tot_pixels_new=[]
    for i in tot_pixels:
        tot_pixels_new += i
            
    # creer la nouvelle image
    img_new= Image.new("RGB",(width, height), "white" )    
    img_new.putdata(tot_pixels_new)
    
    return img_new   
    
        
def find_objects_with_size(img_array, min_height=None, max_height=None, min_width=None, max_width=None):
    
    # Get connected componens and their bounding boxes...
    labels, num_obects = measurements.label(img_array)
    boxes = measurements.find_objects(labels)
    
    # trier les boite avec bonne taille
    panel_boxes = []
    for boxe in boxes:
        if min_height < boxe[0].stop - boxe[0].start or min_height == None: # hauteur min
            if max_height > boxe[0].stop - boxe[0].start or max_height == None: # hauteur max
                if min_width < boxe[1].stop - boxe[1].start or min_width == None: # largeur min
                    if max_width > boxe[1].stop - boxe[1].start or max_width == None: # largeur max
                        panel_boxes.append(boxe) 
            
    return panel_boxes
    
    
def write_text_from_panels(image_array, panels):
    
    # fichier temporaire...
    tmp = os.path.normpath(os.path.expanduser("~/tmp_file.txt"))

    img_content=[]
    nb_column=0 

    # calculer le nombre de colonne
    while True:
        nb_column+=1
        if panels[nb_column][0] != panels[nb_column+1][0]:
            nb_column+=1
            break
   
    for i in range(70):#len(panels)):
        # panels[i] --> coordonnee de chaque boite
        panel_array = image_array[panels[i]]
        
        # transforme array en image et la sauve...
        im = Image.fromarray(panel_array)

        if i<nb_column:
            #pour mieux annalyser
            im=im.convert('1')

        # pour travailler ou se trouve tesseract
        os.chdir('xb_tesseract')
        im.save('img_temp.jpg')
        
        # donner un ordre a la ligne de commande
        if i < nb_column or i % nb_column == 0:
            commande=['tesseract', 'img_temp.jpg', tmp[:-4]]
        else:
            commande=['tesseract', 'img_temp.jpg', tmp[:-4], 'digits']
        output = sp.Popen(commande, stdout=sp.PIPE, shell=True)
        outtext = output.communicate()[0].decode(encoding="utf-8", errors="ignore")
        
        # retourner la ou se trouve le scripte
        os.chdir('..')
        
        # sauvegarder le text de l'image
        f_tmp = open(tmp, 'r')
        text_image = f_tmp.readlines()
        if text_image == []:
            os.chdir('xb_tesseract')
            commande2=['tesseract', 'img_temp.jpg', tmp[:-4], "-psm", "6"]
            output2 = sp.Popen(commande2, stdout=sp.PIPE, shell=True)
            outtext = output2.communicate()[0].decode(encoding="utf-8", errors="ignore")
            os.chdir('..')
            f_tmp = open(tmp, 'r')
            text_image = f_tmp.readlines()
        
        # enlever le saut a la ligne et nombre mal annote
        for i in range(len(text_image)):
            text_image[i] = text_image[i].rstrip('\n').replace('-|','1').replace('\xe2\x80\x94','-')

        img_content.append(str(" ".join(text_image)))
        
        #print img_content, "1" # pour voir ce qui a ete retenu

    # corrige les nombre mal annote       
    for i in range(len(img_content)-nb_column):
        i+=nb_column # pour ne pas corriger la premiere ligne
        if  i%(nb_column) != 0 :
            if '-|' in img_content[i] or 'O' in img_content[i] or ')' in img_content[i] or '-1-' in img_content[i] or '- -' in img_content[i] or '(' in img_content[i] or '+' in img_content[i] or ',' in img_content[i] or ' ' in img_content[i]:
                img_content[i]=img_content[i].replace('-|','1').replace('-1-','').replace('- -','-').replace('O','0').replace('(','').replace(')','').replace('+','').replace(',','.').replace(' ','')

    for i in range(len(img_content)-nb_column):  
        i+=nb_column
        if  i%(nb_column) != 0 and '\xe2' in img_content[i]:
            img_content[i]="-"+img_content[i][3:]
    #print img_content,"2"
        
    # enlever caractere ascii !!!
    for i in range(len(img_content)):
        img_content[i]=img_content[i].replace("\xc3","").replace("\xa9","").replace("\xe2","").replace("\x80","").replace("\x99","").replace("\x98","")
    
    #creer dico pour afficher tableau 
    dict={}
    l=[]
    l_tot=[]
    first_line =[""]
    for i in range(nb_column-1):
        i+=1
        first_line.append('colonne '+str(i))
    dict[' ']=first_line
    l_tot.append(dict)
    dict={}
    compteur = 0
    for i in xrange(len(img_content)):
        l.append(img_content[i])
        if (i+1)%(nb_column)==0:
            if compteur == 0:
                dict[""]=l
            else:
                dict['ligne '+str(compteur)]=l
            l_tot.append(dict)
            compteur += 1
            l=[]
            dict={}
         
    #print l_tot

    return l_tot, nb_column, img_content

    
def creer_doc_xls(data_list, nb_column, path_name):

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('XXX')
    
    line=0
    column=0
    
    #definir des style
    style1 = xlwt.XFStyle()
    style1.num_format_str = "#,##0.00"    
    
    # mettre les valeur dans tableau excel
    for i in range(len(data_list)):
        if column%nb_column == 0:
            ws.write(line, column, data_list[i])
        else:
            ws.write(line, column, data_list[i].replace(".",","), style1)
        column+=1
        if column%nb_column == 0:
            line+=1
            column=0
            
    wb.save("/Users/Xavier/Desktop/"+path_name+".xls") 

    
if __name__ == '__main__':
   app.run(debug = True)