#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication
#from PyQt6 import QtCore
import sys
import time
import Interface  # arquivo *.py gerado pelo pyuic5
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator
import os # interage com o sistema operacional
import dos ## módulo das funções DOS E pDOS
import numpy as np
path = os.path.dirname(os.path.realpath(__file__))
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=9, height=6, dpi=400):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_tight_layout(True)
        self.lin, self.col, self.ID = 1,1,1
        self.axes = self.fig.add_subplot(self.lin, self.col, self.ID)# linha; coluna; posição;
        self.axes.set_facecolor("white")     
        self.axes.set_yticks([])
        self.axes.xaxis.set_minor_locator(AutoMinorLocator(5))
        super(MplCanvas, self).__init__(self.fig)
class App(QtWidgets.QMainWindow, Interface.Ui_MainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)        
        qr=self.frameGeometry()
        self.position = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(self.position)
        self.move(qr.topLeft())
        self.icon1 = QtGui.QIcon()
        self.icon2 = QtGui.QIcon()
        self.icon1.addPixmap(QtGui.QPixmap(path+"/temps/icon1.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
        self.icon2.addPixmap(QtGui.QPixmap(path+"/temps/lupa.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
        self.setWindowIcon(self.icon1)
        self.messageBox = QtWidgets.QMessageBox()
        self.main_widget = QtWidgets.QWidget(self)# progress bar
        self.main_widget.setGeometry(475,30,520,560)# progress bar
#----------------- campo para conectar os módulos às funções ------------------
        self.actionAjuda.triggered.connect(self.AjudaDef)
        self.actionAjuda.setShortcut("F2")
        self.actionSobre.triggered.connect(self.SobreDef)
        self.actionSobre.setShortcut("F3")
        self.actionFechar.triggered.connect(self.FecharDef)
        self.actionFechar.setShortcut("F4")
#------------------------ campo para as funções -------------------------------
        self.search13.clicked.connect(self.ReadDOS)       ## click connect
        self.search13.setIcon(self.icon2)
        self.search13.setToolTip("Pesquisar")
        self.SerieDOS.addItems(["+","-"])
        self.comboDOS.addItems(["DOS","intDOS"])
        self.Calculete13.clicked.connect(self.DOS)
        #-----------------------------------------------------#
        self.search23.clicked.connect(self.ReadPDOS)  
        self.search23.setIcon(self.icon2)
        self.search23.setToolTip("Pesquisar")
        self.SeriePDOS.addItems(["+","-"])
        self.comboPDOS.addItems(["lDOS", "pDOS"])
        self.Calculete23.clicked.connect(self.pDOS)
        self.mono.toggled.connect(self.Magnetic)
        self.mono.toggled.connect(self.Combo)
        self.mono.setToolTip("Selecione somente se o cálculo foi realizado com polarização de spin")
        self.EFermi.setText('0.000')
        #self.EFermi.setAlignment(QtCore.Qt.AlignRight)
        #-----------------------------------------------------#
        self.line_label.setText('Legenda')
        self.s_data.setToolTip("Lista com as séries de dados")
        self.btn_remove.setToolTip("Remove os dados selecionados")
        self.btn_remove.clicked.connect(self.Remove)
        #-----------------------------------------------------#
        self.btn_4.clicked.connect(self.SaveFig) ##
        self.btn_5.clicked.connect(self.Clean) ## conecta a função salvar
        self.btn_6.clicked.connect(self.Salvar) ## conecta a função salvar
        self.btn_7.clicked.connect(self.SaveAll) ## conecta a função salvar
        self.btn_7.setToolTip("Salva todos os dados como uma matriz CSV")
        self.btn_color.clicked.connect(self.color_picker) ##     
        #------------------- área gráfica -------------------------------------
        self.graph = MplCanvas(self, width=16, height=9, dpi=100)
        self.toolbar2 = NavigationToolbar(self.graph, self.frame1)
        self.layout2 = QtWidgets.QVBoxLayout(self.frame1)
        self.layout2.addWidget(self.toolbar2)
        self.layout2.addWidget(self.graph)
        self.grafico2 = QtWidgets.QWidget(self.frame1)
        self.grafico2.setLayout(self.layout2)
        self.grafico2.setGeometry(1, 1, 1197, 603)   
#------------------- Controle de dados ---------------------------------------
        self.data = {} # Dicionário com os arrays
        self.line_color = '#000000'
        self.cont = 1 # Variável de controle
        self.chaves = [] # lista com as chaves
        self.orbitais = None
        self.frame_color.setStyleSheet("background:#000000")
#-----------------------------------------------------------------------------
    def Magnetic(self):
        self.Combo(self.orbitais)
        if self.mono.isChecked() == True:# ativa os orbitais
            self.comboPDOS.clear()
            self.comboPDOS.addItems(["lDOSUP","lDOSDW", "pDOS"])
            self.comboDOS.clear()
            self.comboDOS.addItems(["DOSUP","DOSDW",'pdosup(E)', 'pdosdw(E)'])
        elif self.mono.isChecked() == False:# ativa os orbitais
            self.comboPDOS.clear()
            self.comboPDOS.addItems(["lDOS", "pDOS"])
            self.comboDOS.clear()
            self.comboDOS.addItems(["DOS","intDOS"])
##############################################################################
    def color_picker(self):
        color = QtWidgets.QColorDialog.getColor()
        self.frame_color.setStyleSheet("QWidget { background-color: %s}" % color.name())
        self.line_color = color.name()
    def Combo(self, parameters):
        if parameters == None:
            if self.line_pdosV.text() == '':
                pass
            else:
                self.orbital.clear()
                self.orbital.addItem("Função pDOS inativa!")
        elif parameters == 's':
            if self.mono.isChecked() == False:
                self.orbital.clear()
                self.orbital.addItem("s [column 3]")
            elif self.mono.isChecked() == True:
                self.orbital.clear()
                self.orbital.addItems(["s(up) [column 4]","s(down) [column 5]"])
        elif parameters == 'p':
            if self.mono.isChecked() == False:
                self.orbital.clear()
                self.orbital.addItems(["px [column 3]", "py [column 4]", "pz [column 5]"])
            elif self.mono.isChecked() == True:
                self.orbital.clear()
                self.orbital.addItems(["px(up) [column 4]", "px(down) [column 5]",
                                     "py(up) [column 6]", "py(down) [column 7]",
                                     "pz(up) [column 8]", "pz(down) [column 9]"])
        elif parameters == 'd':
            if self.mono.isChecked() == False:
                self.orbital.clear()
                self.orbital.addItems(["dz2 [column 3]", "dxz [column 4]", "dyz [column 5]",
                                  "dxy [column 6]", "dx2-y2 [column 7]"])
            elif self.mono.isChecked() == True:
                self.orbital.clear()
                self.orbital.addItems(["dz2(up) [column 4]", "dz2(down) [column 5]",
                                  "dxz(up) [column 6]", "dxz(down) [column 7]",
                                 "dyz(up) [column 8]", "dyz(down) [column 9]",
                                 "dxy(up) [column 10]", "dxy(down) [column 11]",
                                 "dx2-y2(up) [column 12]","dx2-y2(down) [column 13]"])
        elif parameters == 'f':
            if self.mono.isChecked() == False:
                self.orbital.clear()
                self.orbital.addItems(["fz3 [column 3]", "fxz2 [column 4]",
                                      "fyz2 [column 5]", "fxyz [column 6]",
                                      "fz [column 7]","fx [column 8]","fy [column 9]"])
            elif self.mono.isChecked() == True:
                self.orbital.clear()
                self.orbital.addItems(["fz3(up) [column 4]", "fz3(down) [column 5]",
                                  "fxz2(up) [column 6]", "fxz2(down) [column 7]",
                                  "fyz2(up) [column 8]", "fyz2(down) [column 9]",
                                  "fxyz(up) [column 10]", "fxyz(down) [column 11]",
                                  "fz(up) [column 12]", "fz(down) [column 13]",
                                  "fx(up) [column 14]", "fx(down) [column 15]",
                                  "fy(up) [column 16]", "fy(down) [column 17]"])
##############################################################################
#------------------------ Funções do D O S -----------------------------------
    def DOS(self):
        X1 = self.SerieDOS.currentText() # serie
        X2 = self.comboDOS.currentText() # tipo de dados
        if self.line_dosV.text() != '': #
            try:
                self.main_widget.progress = QtWidgets.QProgressBar(self)
                self.main_widget.progress.show()
                self.main_widget.progress.setStyleSheet("font-size:10px")
                self.main_widget.progress.setGeometry(2, 620, 1196, 8)
                self.main_widget.progress.setMaximum(100)
                self.main_widget.progress.setValue(59)
                dados = dos.Resp(self.line_dosV.text(),X1,X2,None)
                eV, pdos = dados[0] - float(self.EFermi.text()), dados[1]
                key = self.line_label.text()+'.'+X2+'.'+str(self.cont) # nome da série.
                self.chaves.insert(0, key)
                self.s_data.clear()
                self.s_data.addItems(self.chaves) # adiciona nome no combobox
                self.Grafico(eV, pdos, self.line_color, self.line_label.text()) # plota o gráfico
                self.data[key] = [eV, pdos, self.line_color, self.line_label.text()] # add in dict data array
                self.cont += 1 #atualiza o contador
            except:
                self.messageBox.about(self,"Erro", 'Arquivo(s) incorreto(s)!')
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.setText("Insira o arquivo de saida do cálculo dos.x!")
            msg.setWindowTitle("Atenção")
            msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok )#| QMessageBox.Cancel)
            returnValue = msg.exec()
           # if returnValue == 4194304: # Cancel
                #pass
            if returnValue == 1024: # Ok
                pass
            self.main_widget.progress.close()
    def ReadDOS(self):
        file_dosV, _ = QtWidgets.QFileDialog.getOpenFileNames(None, path, "", "*.*")
        if file_dosV:
            f = []
            for filename in file_dosV:
                f.append(filename+';')
            texto = ''.join(map(str,f))
            if len(f) > 1:
                self.line_dosV.setText(texto)
            else:
                self.line_dosV.setText(f[0])
#---------------------- Funções do p D O S -----------------------------------
    def pDOS(self):
        try:
            if self.comboPDOS.currentText() == 'pDOS':
                Y1 = self.SeriePDOS.currentText()
                Y2 = 'pDOS'
                Y3 = self.orbital.currentText()
            else:
                Y1 = self.SeriePDOS.currentText() # série
                Y2 = self.comboPDOS.currentText() # tipo de dado
                Y3 = None
            if self.line_pdosV.text() != '':
                self.main_widget.progress = QtWidgets.QProgressBar(self)
                self.main_widget.progress.show()
                self.main_widget.progress.setStyleSheet("font-size:10px")
                self.main_widget.progress.setGeometry(2, 620, 1196, 8)
                self.main_widget.progress.setMaximum(100)
                self.main_widget.progress.setValue(53)
                #---------- leitura dos dados --------------------------------
                dados = dos.Resp(self.line_pdosV.text(),Y1,Y2,Y3)
                eV, pdos = dados[0] - float(self.EFermi.text()), dados[1]
                #self.texto.setText(str(np.transpose([eV,pdos]))) # insere dados na área de texto
                key = self.line_label.text()+'.'+Y2+'.'+str(self.cont) # nome da série.
                self.chaves.insert(0, key)
                self.s_data.clear()
                self.s_data.addItems(self.chaves) # adiciona nome no combobox
                self.Grafico(eV, pdos, self.line_color, self.line_label.text()) # plota o gráfico
                self.data[key] = [eV, pdos, self.line_color, self.line_label.text()] # add in dict data array
                #self.data_text[key] = dados[0] # add in dict text
                self.cont += 1 #atualiza o contador
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                msg.setText("Insira o arquivo de saida do cálculo projwfc.x!")
                msg.setWindowTitle("Atenção")
                msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok )#| QMessageBox.Cancel)
                returnValue = msg.exec()
               # if returnValue == 4194304: # Cancel
                    #pass
                if returnValue == 1024: # Ok
                    pass
        except:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.setText("nenhum arquivo inserido!")
            msg.setWindowTitle("Atenção")
            msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok )#| QMessageBox.Cancel)
            returnValue = msg.exec()
           # if returnValue == 4194304: # Cancel
                #pass
            if returnValue == 1024: # Ok
                pass
            self.main_widget.progress.close()
#------------------------------------------------------------------------------
    def ReadPDOS(self):
        #---------------------------------------------------------------------
        def Orbital(file):
            var = file.split(';')
            var.pop()
            orbitais = []
            materiais = []
            for i in var:
                materiais.append(i.split('/').pop())
            for j in materiais:
                orbitais.append(j.split('(').pop()[0])
            materiais.clear()
            for k in orbitais:
                if k not in materiais:
                    materiais.append(k)
            if len(materiais)>1:
                return None
            elif len(materiais) == 1:
                return materiais[0]
        #---------------------------------------------------------------------
        file_pdosV, _ = QtWidgets.QFileDialog.getOpenFileNames(None, path, "", "*.*")
        if file_pdosV:
            f = []
            for filename in file_pdosV:
                f.append(filename+';')
            texto = ''.join(map(str,f))
            self.line_pdosV.setText(texto)#f[0])
            self.orbitais = Orbital(self.line_pdosV.text())
            self.Combo(self.orbitais) ##############
#--------------------------- B U T T O N S  2 ---------------------------------
    def Clean(self):
        self.line_pdosV.clear()
        self.line_dosV.clear()
        self.orbitais = None
        self.orbital.clear()
        self.s_data.clear()
        self.graph.axes.clear()
        self.graph.axes.set_yticks([])
        self.graph.fig.canvas.draw()    
        self.data.clear()
        self.chaves.clear()
        self.line_color = '#000000'
        self.frame_color.setStyleSheet("background:#000000")
        self.cont = 1
    def Salvar(self):
        try:
            self.fileName2, _ = QtWidgets.QFileDialog.getSaveFileName(None, path, ".csv","CSV files (*.csv);;",)
            x = self.data[self.s_data.currentText()][0]
            y = self.data[self.s_data.currentText()][1]
            np.savetxt(self.fileName2, np.transpose([x,y]), delimiter=',', fmt='%3.5E')
        except: pass
    def SaveAll(self):        
        try:
            self.fileName3, _ = QtWidgets.QFileDialog.getSaveFileName(None, path, ".csv","CSV files (*.csv);;",)
            labels = ['#Energia']
            x = []
            y = []
            c = self.data #dicionario com os dados
            for i in c:
                labels.append(i.split('.')[0])
                x.append(c[i][0])
                y.append(c[i][1])
            x = x[0]
            y.insert(0, x)
            dados = np.transpose(y)
            l1 = ",".join(map(str,labels))
            with open(self.fileName3, 'w') as output:
                output.write(l1+'\n')
                np.savetxt(output, dados, delimiter=',', fmt='%3.5E')
        except: pass
###############################################################################
    def Grafico(self, a, b, c, d):
        self.Progress()########################
        self.graph.axes.plot(a, b, color = c, label=d, linewidth=1)
        self.graph.axes.set_xlabel('E - E$_{Fermi}$ (eV)')
        self.graph.axes.legend()
        self.graph.axes.set_yticks([])
        self.graph.fig.canvas.draw()     
    def SaveFig(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Salvar como', '.png', '*.png')
        print(path)
        if path != ('', ''):
            self.graph.fig.savefig(path[0],dpi=400)
    def Remove(self):
        try:
            self.graph.axes.clear()              
            self.data.pop(self.s_data.currentText()) # remove data of dict
            self.chaves.remove(self.s_data.currentText())
            self.s_data.removeItem(self.s_data.currentIndex())
            if len(self.data) > 0:
                self.cont = self.cont - 1
                for i in self.data:
                    x, y, c, d = self.data[i][0], self.data[i][1], self.data[i][2], self.data[i][3]
                    self.graph.axes.plot(x,y, color=c, label=d, linewidth=1)
                    self.graph.axes.set_xlabel('E - E$_{Fermi}$ (eV)')
                    self.graph.axes.legend()
                    self.graph.axes.set_yticks([])
                    self.graph.fig.canvas.draw()
            elif len(self.data) == 0:
                    self.s_data.clear()
                    self.data.clear()
                    self.chaves.clear()
                    self.cont = 1                 
                    self.line_color = '#000000'
                    self.chaves.clear()
                    self.graph.axes.clear()   
                    self.graph.axes.set_yticks([])
                    self.graph.fig.canvas.draw()   
        except: pass
    def Progress(self):
        TIME_LIMIT = 100
        count = 62
        while count < TIME_LIMIT:
            count += 1
            time.sleep(0.001)
            self.main_widget.progress.setValue(count)
        self.main_widget.progress.close()
#######################  funções barra de menu   ##############################
    def FecharDef(self):
        self.close()
    def SobreDef(self):
        self.messageBox.about(self, 'Sobre', '''
Este programa foi desenvolvido para analizar:
         i) densidade de estados (DOS).
        ii) densidade de estados projetada (pDOS).
Ele é compatível com outputs dos códigos dos.x e projwfc.x das versões 6x do QuantumESPRESSO.
Tenha cuidado ao usá-lo com dados vindos de outras versões.\n\n
autor: Márcio F. Santos
email: marciofs600@gmail.com''')
    def AjudaDef(self):
        self.messageBox.about(self, 'Ajuda', """# Notas de Uso:
    Conjunto DOS:
       Esse bloco deve ser usado para tratar os dados provenientes de um 
       cálculo dos.x. Nele é possível plotar a densidade total, bem como
       a densidade integrada(DOS e intDOS). O painel série (+) e (-) serve
       para inverter o sinal do gráfico (Geralmente usa-se a série(-) para
       plotar gráfico de spin down, [vide spin polarizado])
    Conjunto pDOS:
        
""")
#------------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec()

if __name__ == '__main__':
    main()
