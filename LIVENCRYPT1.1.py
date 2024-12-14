# LIVENCRYPT 1.1 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# LIVENCRYPT 1.1 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LIVENCRYPT 1.1. If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2024 Synergia86

import io
import tempfile
import os
import shutil
import json
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import binascii
import tkinter.font as tkFont
from PIL import Image, ImageDraw, ImageTk
import string
import random
import zipfile

def get_base_path():
    """Get the base path where the executable is running."""
    if getattr(sys, 'frozen', False):
        # Estamos en un ejecutable creado por PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Estamos en un script normal
        return os.path.dirname(os.path.abspath(__file__))

def get_data_path():
    base_path = get_base_path()
    plantillas_path = os.path.join(base_path, "ficheros Livencrypt")
    
    if not os.path.exists(plantillas_path):
        try:
            os.makedirs(plantillas_path)
        except Exception as e:
            plantillas_path = os.path.join(os.path.expanduser("~"), ".livencrypt", "ficheros Livencrypt")
            os.makedirs(plantillas_path, exist_ok=True)
    
    return plantillas_path

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Ejemplo de cómo usar un string Unicode
some_string = u"Este es un string Unicode"

# Ejemplo de cómo abrir un archivo con codificación UTF-8
# (Este bloque debe estar dentro de una función o método donde se use)
# def some_function(filename):
#     with open(filename, 'w', encoding='utf-8') as f:
# 

class LIVENCRYPT(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plantillas_personalizadas = {}
        self.teclados = {}
        self.correspondencia_plantillas = {}
        self.memoria_cifrado = []
        self.opcion = tk.StringVar(value="cifrar")
        self.is_binary = False  # Suponiendo que hay un atributo que indica si el archivo es binario
        self.original_filename = ""  # Nombre original del archivo
        self.total_chars = 0
        self.medida_fuente = 14
        self.idioma_actual = "Español"
        self.widgets_traducibles = []
        self.botones_caracteres = {}
        self.caracteres_usados = set()
        self.directorio_plantillas = get_data_path()
        self.geometry("800x600")
        self.iconphoto(True, ImageTk.PhotoImage(Image.open(resource_path("icono.png"))))
        self.cargar_traducciones()  # Asume que este método carga las traducciones necesarias
        self.cargar_plantillas()  # Carga las plantillas desde el directorio
        self.plantilla = ttk.Combobox(self, font=("TkDefaultFont", self.medida_fuente))
        self.crear_widgets()  # Crear widgets, incluye configuración inicial del Combobox
        self.actualizar_lista_plantillas()  # Actualiza el Combobox con las plantillas cargadas
        self.configurar_estilos()  # Configura los estilos después de crear y actualizar widgets
        self.subcategoria_actual = None

        self.definir_faq_texto()
        self.definir_consejos_texto()

    def crear_directorio_plantillas(self):
        """Create the 'Plantillas' directory if it does not exist."""
        if not os.path.exists(self.directorio_plantillas):
            os.makedirs(self.directorio_plantillas)

    def cargar_plantillas(self):
        """Load templates from JSON files in the 'Plantillas' directory."""
        self.plantillas_personalizadas.clear()
        if not os.path.exists(self.directorio_plantillas):
            return
    
        for archivo in os.listdir(self.directorio_plantillas):
            if archivo.endswith('.json'):
                nombre_plantilla = os.path.splitext(archivo)[0]
                ruta_archivo = os.path.join(self.directorio_plantillas, archivo)
                try:
                    with open(ruta_archivo, 'r', encoding='utf-8') as f:
                        plantilla = json.load(f)
                    self.plantillas_personalizadas[nombre_plantilla] = plantilla
                    print(f"Plantilla cargada: {nombre_plantilla}")
                except Exception as e:
                    print(f"Error al cargar la plantilla {nombre_plantilla}: {e}")

    def icono(self):
        """Cargar y configurar el icono de la aplicación."""
        return ImageTk.PhotoImage(Image.open(resource_path("icono.png")))
            
    def abrir_nueva_ventana(self):
        nueva_ventana = tk.Toplevel(self)
        nueva_ventana.title("Nueva Ventana")
        nueva_ventana.geometry("400x300")
        nueva_ventana.iconphoto(True, self.load_icon())

    def definir_faq_texto(self):
        self.faq_texto = {
                "Español": """
        # ¿Para qué sirve LIVENCRYPT?
        LIVENCRYPT sirve para mantener conversaciones 100% privadas. Ahora eres tú el primer nivel de seguridad creando un cifrado del contenido y solo el destinatario sabrá la frecuencia para descifrar el contenido.
    
        # ¿No hay manual para usar LIVENCRYPT?
        Cifrar texto: texto sin cifrar pasará a ser cifrado. 
        Descifrar texto: texto cifrado pasará a ser descifrado. 
        En Valor: solo números del 0 al 1000. 
        Selecciona la plantilla que contenga los caracteres añadidos en el texto y le das a ejecutar para que te muestre el resultado. 
        Contraseña: En esta versión si en el texto añades uno de los siguientes caracteres especiales: ¢|@#~½¶←↓→ˀ|¢ª─¬ te solicitará insertar contraseña al ejecutar y tendrás que añadir el carácter especial del texto y los 7 siguientes caracteres (el espacio también cuenta como carácter). Ejemplo: hola~1234567890 te solicitará insertar contraseña = ~1234567 y al validarse se cifrará el texto. Con el texto cifrado al usar la función descifrar tendrás que recordar la contraseña, en este caso para que se ejecute el descifrado tendrás que introducir ~1234567.
        Gestionar plantillas: crear plantillas, al seleccionar un idioma mostrará los caracteres para añadirlos individualmente o usar el botón agregar todos. En Números/signos encontrarás los números y signos de los idiomas. Como carácter especial está el espacio "␣" para que se ejecute en el cifrado, si no se añade y uses el espacio te dejará espacios en el cifrado.
        Seleccionar tamaño: se trata las filas y columnas que tendrá la plantilla. Puedes utilizar los valores por defecto o puedes añadir los valores que desees pero para poder guardar la plantilla tendrás que dejar el contador de caracteres a cero.
        Aleatorizar: mueve aleatoriamente los caracteres añadidos.
        Limpiar: Elimina todos los caracteres añadidos.
        Borrar último carácter.
        Guardar plantilla: indicar el nombre de la plantilla y guardar.
        Para editar te saldrá solamente las plantillas creadas. Solo podrás eliminar las plantillas que hayas creado. Las plantillas que están por defecto podrás verlas viendo el código fuente.
        En el principal hay un icono en la esquina superior derecha para acceder a los ajustes. Se cambia el idioma, se cambia el tamaño de la letra entre un valor de 8 y 24. Preguntas frecuentes, consejos, créditos y licencia.

        # Para cifrar o descifrar un fichero. Selecciona la función a realizar, carga el fichero, inserta los valores, ejecuta tantas veces como sea necesario (recomendable mínimo realizar 2 cifrados) y guardar fichero. En modo cifrado se guardarán los ficheros en hexadecimal .txt, en modo descifrar te solicitará la extensión del fichero que debe de tener y en la siguiente ventana lo guardará en binario.
    
        # ¿Es complicado compartir una nueva plantilla con otra persona y que coincidan la posición de todos los caracteres?
        No, tan solo tienes que indicarle el tamaño (filas/columnas) y compartir todos los caracteres separados por una coma y guardar plantilla. Con tener una secuencia de cifrado usando las plantillas por defecto puedes pegar los caracteres de la nueva plantilla y enviarle la nueva plantilla cifrada.
    
        # No puedo quedar con la persona para indicarle la colocación de los caracteres en la plantilla que he creado, ¿Qué puedo hacer?
        Si no podéis quedar en persona os lo tenéis que ingeniar para intercambiaros la secuencia de valores de tal manera que si el algoritmo repasa vuestras conversaciones pasase por alto que estáis compartiendo valores y de ser consciente de ello no usar el mismo medio, sino diferentes y con instrucciones que solo ambos entenderéis alteren los valores pero el algoritmo no sea capaz de interpretar que tiene relación con los valores. Además de usar las plantillas por defecto y una vez tengáis la secuencia ya podéis crear nuevas plantillas dando detalles en los mensajes cifrados.
    
        # ¿Aportarías más cambios?
        Sí, he pensado añadir un control sobre los valores de la contraseña y poder añadir/editar los caracteres que puedan asignarse como contraseña. Copia y pega un carácter especial en el texto si quieres activar la contraseña en tu cifrado aunque tu idioma no te facilite el carácter. 
        
        # ¿Estará traducido en más idiomas?
        Sí, seguiré trabajando para que esté accesible para todos. Acceder al discord.gg/sDRawvyXhy y solicitar vuestro idioma. Aunque siendo sincero, no hace falta que LIVENCRYPT esté en tu idioma, es muy intuitivo, incluso creando una plantilla nueva te permite añadir caracteres nuevos que no estén en los idiomas listados.
    
        # ¿Se crearán nuevas formas de compartir el cifrado?
        Sí, tengo en mente interacción en escenarios virtuales creados por IA con opción de conversación por voz usando web3 y conexiones P2P. Los escenarios serían únicos y eliminados al finalizar la sesión.
        
        # ¿Qué requisitos tiene la aplicación?
        Se puede usar sin tener acceso a Internet y se podría usar la tecnología que se usó para llegar a la luna y funcionaria perfectamente, desgraciadamente la tecnología desapareció y ya no se puede volver a la luna pero sí podrás usar LIVENCRYPT en cualquier dispositivo por muy antiguo que sea. Incluso si tienes la plantilla y los valores de las secuencias podrías cifrarlo y descifrarlo manualmente.
        
        # ¿Se puede usar LIVENCRYPT para enviar fotos, vídeos, audios encriptados?
        Obviamente ahora no, pero igual el día de mañana sí.
    
        # No hay anuncios ni es de pago la aplicación ¿Dónde está el truco?
        Nos han hecho creer que si algo no tiene valor y lo puede tener cualquiera no vale nada para uno mismo. Sin embargo usamos plataformas "gratuitas" y en el sistema no hay nada gratuito, pues cada uno de nosotros somos un producto para ellos y el algoritmo va recopilando todas nuestras acciones para luego vendernos nuestros intereses o cualquier cosa que hayamos comentado mediante publicidad. Si quieres crear un bien para la Humanidad no hay mayor gozo que TODO SER HUMANO lo utilice sin ningún impedimento. Por lo que estaré agradecido por aquellos que compartan la aplicación, la utilicen y por aquellos que quieran aportar su gratitud con donaciones comparto las siguientes wallet:
        ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
        Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
        
        # ¿Por qué licencia GPLv3?
        Por transparencia demostrando que no hay puerta trasera ni nada sospechoso y para que cualquiera pueda aportar su grano de arena en mejorar LIVENCRYPT.
    
        # ¿Dónde se puede ver el código original?
        El código LIVENCRYPT 1.1 lo encontrarás en: github.com/Synergia86 y gitee.com/Synergia_0ef4
    
        # ¿Me gustaría reportar errores y sugerencias de ideas?
        Puedes no tener ni idea de programar pero si quieres colaborar, accede a la comunidad de discord.gg/sDRawvyXhy para compartir los errores e ideas que tengas en mente.
    
        # Cualquier programador de verdad se va a reír del código.
        Para nada me sorprendería y algunos hasta se estirarán de los pelos de los genitales tras analizar todo el código. Lo he creado usando chatgpt y claude.ai, tengo que decir que no ha sido nada fácil, mucha calma y perseverancia ante miles de pruebas y errores. Me formé en informática pero no en la rama de programador, perdonarme por no respetar la estructura. Lo más importante es que FUNCIONA.
    
        # No tengo nada que ocultar, soy un buen esclavo obediente a lo que me digan las autoridades.
        Algún día agradecerás a la HUMANIDAD que decidió dar el paso para hacer de esta realidad una mejor para el beneficio común de todos. Puedes recorrer tu camino como un NPC o puedes dejar tu huella y sabes lo mejor? Qué ambos caminos son igual de válidos!
    
        # El sistema me investigará si uso la aplicación.
        El sistema tiene un registro detallado de cada SER HUMANO desde que nace y si no hacemos nada acabaremos pagando por respirar.
        
        # Los genios que han contribuido en un bien por la Humanidad han acabado teniendo accidentes mortales, ¿Tienes miedo de que te puede pasar algo?
        Si tuviera miedo LIVENCRYPT no habría salido a la luz. Aquí estamos para dejar nuestra huella y si me tengo que marchar volveré en otra vida para seguir tocando los cojones. Cuanto más miedo quieren que tengamos es cuando más nos tenemos que reír del show que nos creen. ¡Infundir miedo y creérselo también nos mata! ¡Reíros y disfrutad del camino!
                """,
                "English": """
        # What is LIVENCRYPT for?
        LIVENCRYPT is used to maintain 100% private conversations. Now you are the first level of security by creating encryption of the content and only the recipient will know the frequency to decrypt the content.
        
        # Is there no manual for using LIVENCRYPT?
        Encrypt text: unencrypted text will become encrypted.
        Decrypt text: encrypted text will become decrypted.
        In Value: only numbers from 0 to 1000.
        Select the template containing the added characters in the text and click run to see the result.
        Password: In this version, if you add one of the following special characters to the text: ¢|@#~½¶←↓→ˀ|¢ª─¬ you will be prompted to insert a password upon execution. You will need to add the special character from the text and the next 7 characters (space also counts as a character). Example: hello~1234567890 will prompt you to insert password = ~1234567, and upon validation, the text will be encrypted. With the encrypted text, using the decrypt function, you will need to remember the password; in this case, to execute decryption, you will need to enter ~1234567.
        Manage templates: create templates; selecting a language will show the characters to add individually or use the add all button. In Numbers/signs you will find the numbers and signs of the languages. As a special character, there is the space "␣" to be executed in encryption; if not added and you use space, it will leave spaces in the encryption.
        Select size: this refers to the rows and columns that the template will have. You can use the default values or add the values you want, but to save the template, you must leave the character counter at zero.
        Randomize: randomly moves the added characters.
        Clear: removes all added characters.
        Delete last character.
        Save template: indicate the name of the template and save.
        To edit, only the templates you have created will appear. You can only delete the templates you have created. The default templates can be seen by viewing the source code.
        In the main interface, there is an icon in the upper right corner to access settings. You can change the language, change the font size between a value of 8 and 24. Frequently asked questions, tips, credits, and license.

        # To encrypt or decrypt a file. Select the function to perform, upload the file, insert the values, run as many times as necessary (it is recommended to perform at least 2 encryptions), and save the file. In encryption mode, the files will be saved in hexadecimal .txt, in decryption mode, it will ask you for the file extension and in the next window, it will save it in binary.
        
        # Is it complicated to share a new template with someone and have all characters' positions match?
        No, you just need to provide the size (rows/columns) and share all the characters separated by a comma and save the template. With a sequence of encryption using default templates, you can paste the characters of the new template and send them the new encrypted template.
        
        # I can't meet with the person to show them the placement of characters in the template I created, what can I do?
        If you cannot meet in person, you need to figure out how to exchange the sequence of values so that if the algorithm reviews your conversations, it overlooks that you are sharing values. If aware of this, do not use the same medium but different ones, and with instructions that only both of you understand, alter the values in a way that the algorithm cannot interpret that they are related to the values. Besides using default templates, once you have the sequence, you can create new templates by providing details in the encrypted messages.
        
        # Would you add more changes?
        Yes, I have thought about adding control over the password values and being able to add/edit the characters that can be assigned as a password. Copy and paste a special character in the text if you want to activate the password in your encryption even if your language does not provide the character.
        
        # Will it be translated into more languages?
        Yes, I will continue working to make it accessible to everyone. Join the discord.gg/sDRawvyXhy and request your language. Although, to be honest, LIVENCRYPT doesn't need to be in your language; it is very intuitive. Even creating a new template allows you to add new characters not shown in the available languages.
        
        # Will new ways of sharing encryption be created?
        Yes, I am thinking of interaction in virtual scenarios created by AI with voice conversation options using web3 and P2P connections. The scenarios would be unique and deleted after the session ends.
        
        # What are the application requirements?
        It can be used without internet access and could use the technology that was used to reach the moon and work perfectly. Unfortunately, the technology has disappeared, and we can't return to the moon, but you can use LIVENCRYPT on any device, no matter how old it is. Even if you have the template and sequence values, you could encrypt and decrypt manually.
        
        # Can LIVENCRYPT be used to send encrypted photos, videos, audio?
        Obviously not now, but maybe someday in the future.
        
        # There are no ads, and the app is free. Where’s the catch?
        We have been made to believe that if something has no value and anyone can have it, it is worthless to oneself. However, we use "free" platforms, and in the system, nothing is free; each of us is a product for them, and the algorithm collects all our actions to later sell us our interests or anything we have mentioned through advertising. If you want to create a good for humanity, there is no greater joy than EVERY HUMAN using it without any impediment. Therefore, I would be grateful to those who share the app, use it, and for those who wish to express their gratitude through donations, I share the following wallets: 
        ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
        Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
        
        # Why GPLv3 license?
        For transparency, demonstrating that there is no backdoor or anything suspicious and so that anyone can contribute their grain of sand to improve LIVENCRYPT.
        
        # Where can the original code be seen?
        You will find the LIVENCRYPT 1.1 code at: github.com/Synergia86 and gitee.com/Synergia_0ef4
        
        # Would you like to report errors and suggest ideas?
        You may not know how to program, but if you want to collaborate, join the discord.gg/sDRawvyXhy community to share any errors and ideas you have in mind.
        
        # Any real programmer would laugh at the code.
        I wouldn't be surprised, and some might even pull their hair out after analyzing the code. I created it using ChatGPT and Claude.ai. I must say it was not easy, a lot of calm and perseverance through thousands of tests and errors. I trained in IT but not in programming, so I apologize for not respecting the structure. The most important thing is that IT WORKS.
        
        # I have nothing to hide; I am a good, obedient slave to what the authorities tell me.
        Someday you will thank HUMANITY for taking the step to make this reality better for the common benefit of all. You can walk your path like an NPC or leave your mark, and you know what? Both paths are equally valid!
        
        # The system will investigate me if I use the application.
        The system has a detailed record of every HUMAN from birth, and if we do nothing, we will end up paying for breathing.
        
        # Geniuses who have contributed to the good of humanity have ended up having fatal accidents. Are you afraid something might happen to you?
        If I were afraid, LIVENCRYPT would never have come to light. Here we are to leave our mark, and if I have to leave, I will return in another life to keep causing trouble. The more fear they want us to have, the more we need to laugh at the show they create. Infusing fear and believing it also kills us! Laugh and enjoy the journey!
                """,
                "中文": """
        # LIVENCRYPT的用途是什么？
        LIVENCRYPT 用於維持 100% 的私密對話。現在，您可以透過建立內容加密來實現第一層安全，並且只有收件者知道解密內容的頻率。
        
        # 没有使用LIVENCRYPT的手册吗？
        加密文本：未加密的文本将变为加密文本。
        解密文本：加密的文本将变为未加密文本。
        在值中：仅限从零到一千的数字。
        选择包含文本中添加的字符的模板，然后点击运行以查看结果。
        密码：在此版本中，如果您在文本中添加以下特殊字符之一：¢|@#~½¶←↓→ˀ|¢ª─¬ 执行时将提示您输入密码。您需要添加文本中的特殊字符和接下来的七个字符（空格也算作一个字符）。例如：你好~一二三四五六七八九零 将提示您输入密码 = 〜一二三四五六七 并在验证后加密文本。对于加密文本，使用解密功能时，您需要记住密码；在这种情况下，要执行解密，您需要输入 〜一二三四五六七。
        管理模板：创建模板；选择一种语言将显示要单独添加的字符或使用“添加所有”按钮。在数字/符号中，您将找到语言的数字和符号。作为特殊字符，空间"␣"将用于加密；如果未添加并使用空格，它将留下加密中的空格。
        选择大小：这指的是模板的行和列。您可以使用默认值或添加所需的值，但要保存模板，必须将字符计数器保持在零。
        随机化：随机移动添加的字符。
        清除：删除所有添加的字符。
        删除最后一个字符。
        保存模板：指明模板名称并保存。
        编辑时，只会显示您创建的模板。您只能删除自己创建的模板。默认模板可以通过查看源代码来查看。
        在主界面上，右上角有一个图标可以访问设置。您可以更改语言，字体大小可以在八到二十四之间更改。常见问题、提示、致谢和许可。

        要加密或解密文件。选择要执行的功能，上传文件，输入值，运行所需的次数（建议至少执行2次加密），并保存文件。在加密模式下，文件将以十六进制.txt格式保存，在解密模式下，它会要求你输入文件的扩展名，并在下一个窗口中以二进制格式保存。
        
        # 与别人分享新模板并让所有字符的位置匹配是否复杂？
        不，您只需提供大小（行/列）并分享所有字符，字符之间用逗号分隔，然后保存模板。使用默认模板的加密序列，您可以粘贴新模板的字符并将新加密模板发送给他们。
        
        # 我无法与人见面以显示我创建的模板中的字符位置，我该怎么办？
        如果您不能亲自见面，您需要找出如何交换值序列，以便如果算法检查您的对话，它会忽略您正在共享的值。如果意识到这一点，不要使用相同的媒介，而是使用不同的媒介，并用只有您和对方能够理解的指令改变值，以便算法无法解释这些值是相关的。除了使用默认模板，一旦您拥有序列，您可以创建新模板并在加密消息中提供详细信息。
        
        # 您会添加更多更改吗？
        是的，我考慮過添加對密碼值的控制，並能夠添加/編輯可以指定為密碼的字元。如果您想在加密中啟動密碼，即使您的語言不提供特殊字符，也可以在文字中複製並貼上該字符。
        
        # 会翻译成更多语言吗？
        会的，我将继续努力让它对所有人都可用。加入discord.gg/sDRawvyXhy并请求您的语言。虽然老实说，LIVENCRYPT不需要在您的语言中；它非常直观。即使创建新模板，也允许您添加在可用语言中未显示的新字符。
        
        # 会创建新的加密分享方式吗？
        是的，我正在考虑在由AI创建的虚拟场景中进行互动，使用網路三和點對點连接进行语音对话选项。这些场景将是独特的，并在会话结束后被删除。
        
        # 应用程序的要求是什么？
        它可以在没有互联网连接的情况下使用，并且可以使用到达月球时使用的技术，并且可以完美运行。不幸的是，这项技术已经消失，我们不能返回月球，但您可以在任何设备上使用LIVENCRYPT，无论设备多么古老。即使您拥有模板和序列值，您也可以手动加密和解密。
        
        # LIVENCRYPT 可以用來傳送加密的照片、影片、音訊嗎？
        显然现在不能，但也许将来可以。
        
        # 没有广告，也不收费，哪里有问题？
        我们被灌输这样的观念：如果某样东西没有价值，任何人都可以拥有，那对自己来说也没有价值。然而，我们使用的“免费”平台，系统中没有任何东西是免费的；我们每个人都是他们的产品，算法收集我们所有的行为，然后通过广告将我们的兴趣或我们提到的任何事情卖给我们。如果您想为人类创造福祉，没有比每个人都能无障碍使用它更大的喜悦。因此，我对那些分享应用程序、使用它的人，以及那些希望通过捐赠表达感激的人表示感谢，我分享以下钱包：
        以太坊 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
        日光浴室 FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        比特幣 bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        門羅幣 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
        
        # 为什么使用GPLv3许可证？
        为了透明，证明没有后门或任何可疑之处，并且任何人都可以为改进LIVENCRYPT贡献自己的一份力量。
        
        # 哪里可以查看原始代码？
        LIVENCRYPT 1.1 的代码可以在 github.com/Synergia86 和 gitee.com/Synergia_0ef4
        
        # 您想报告错误并提出建议吗？
        即使您可能不了解编程，但如果您想合作，可以加入discord.gg/sDRawvyXhy社区，分享您遇到的错误和想法。
        
        # 任何真正的程序员都会对代码发笑。
        我不会感到惊讶，有些人可能在分析代码后甚至会揪心。 我是用ChatGPT和Claude.ai创建的。我必须说这并不容易，需要通过数千次测试和错误保持冷静和毅力。我接受了IT培训，但不是编程方面的培训，因此对不起没有遵守结构。最重要的是它能正常工作。
        
        # 我没有什么可隐藏的，我是一个听从当局命令的好奴隶。
        总有一天你会感谢人类，感谢他们采取了措施使这个现实变得更好，以造福所有人。你可以像非玩家角色一样走自己的路，也可以留下你的痕迹，你知道吗？这两条道路都是同样有效的！
        
        # 如果我使用应用程序，系统会调查我吗？
        系统对每个从出生开始的人都有详细记录，如果我们什么都不做，我们将最终为呼吸付出代价。
        
        # 为人类做出贡献的天才最终都遇到致命事故。你担心会发生什么事吗？
        如果我害怕，LIVENCRYPT就不会问世了。我们在这里留下我们的印记，如果我不得不离开，我会在另一个生命中回来继续捣乱。他们越想让我们害怕，我们就越要对他们制造的表演大笑。注入恐惧并相信它也会杀死我们！笑一笑，享受这个旅程！
                """,
                "हिन्दी": """
        # LIVENCRYPT का क्या उपयोग है?
        LIVENCRYPT १००% निजी बातचीत को बनाए रखने के लिए उपयोगी है। अब आप सुरक्षा का पहला स्तर हैं, सामग्री को एन्क्रिप्ट करके और केवल प्राप्तकर्ता को सामग्री को डिक्रिप्ट करने की आवृत्ति पता होगी।
    
        # LIVENCRYPT का उपयोग करने के लिए कोई मैनुअल नहीं है?
        टेक्स्ट एन्क्रिप्ट करें: बिना एन्क्रिप्ट किया गया टेक्स्ट एन्क्रिप्टेड हो जाएगा।
        टेक्स्ट डिक्रिप्ट करें: एन्क्रिप्टेड टेक्स्ट डिक्रिप्टेड हो जाएगा।
        मान में: केवल नंबर ज़ीरो से लेकर एक हजार तक।
        उस टेम्पलेट का चयन करें जिसमें टेक्स्ट में जोड़े गए वर्ण हों और परिणाम देखने के लिए चलाएँ।
        पासवर्ड: इस संस्करण में, यदि आप टेक्स्ट में निम्नलिखित विशेष वर्ण जोड़ते हैं: ¢|@#~½¶←↓→ˀ|¢ª─¬, तो आपको कार्यान्वयन के समय पासवर्ड दर्ज करने के लिए कहा जाएगा। आपको टेक्स्ट से विशेष वर्ण और अगले सात वर्ण (स्पेस भी एक वर्ण के रूप में गिना जाता है) जोड़ना होगा। उदाहरण: नमस्ते~१२३४५६७८९० आपको पासवर्ड दर्ज करने के लिए कहेगा = ~१२३४५६७ और मान्यता के बाद, टेक्स्ट एन्क्रिप्टेड हो जाएगा। एन्क्रिप्टेड टेक्स्ट के साथ, डिक्रिप्ट फ़ंक्शन का उपयोग करते समय, आपको पासवर्ड याद रखना होगा; इस मामले में, डिक्रिप्शन को कार्यान्वित करने के लिए आपको ~१२३४५६७ दर्ज करना होगा।
        टेम्पलेट प्रबंधित करें: टेम्पलेट बनाएं; एक भाषा का चयन करने पर व्यक्तिगत रूप से जोड़ने के लिए वर्ण दिखाए जाएंगे या सभी जोड़ने के बटन का उपयोग करें। संख्याएँ/चिन्ह में आप भाषाओं के नंबर और चिन्ह पाएंगे। एक विशेष वर्ण के रूप में, "␣" स्थान एन्क्रिप्शन में निष्पादित किया जाएगा; यदि जोड़ा नहीं जाता और आप स्थान का उपयोग करते हैं, तो एन्क्रिप्शन में स्थान छोड़ देगा।
        आकार चुनें: यह उन पंक्तियों और स्तंभों को संदर्भित करता है जो टेम्पलेट में होंगे। आप डिफ़ॉल्ट मानों का उपयोग कर सकते हैं या आप जो मान चाहें जोड़ सकते हैं, लेकिन टेम्पलेट को सहेजने के लिए आपको वर्ण गिनती को शून्य पर छोड़ना होगा।
        यादृच्छिक करें: जोड़े गए वर्णों को यादृच्छिक रूप से ले जाता है।
        साफ़ करें: सभी जोड़े गए वर्णों को हटा देता है।
        अंतिम वर्ण हटाएं।
        टेम्पलेट सहेजें: टेम्पलेट का नाम निर्दिष्ट करें और सहेजें।
        संपादित करने के लिए, केवल वे टेम्पलेट दिखेंगे जो आपने बनाए हैं। आप केवल उन टेम्पलेट को हटा सकते हैं जो आपने बनाए हैं। डिफ़ॉल्ट टेम्पलेट को आप स्रोत कोड देख कर देख सकते हैं।
        मुख्य इंटरफेस में, सेटिंग्स तक पहुँचने के लिए ऊपरी दाएँ कोने में एक आइकन है। आप भाषा बदल सकते हैं, फ़ॉन्ट आकार को आठ से लेकर चौबीस तक बदल सकते हैं। सामान्य प्रश्न, सुझाव, क्रेडिट और लाइसेंस।

        # एक फाइल को एन्क्रिप्ट या डिक्रिप्ट करने के लिए। करने के लिए कार्य का चयन करें, फाइल को लोड करें, मान दर्ज करें, आवश्यकतानुसार कई बार चलाएँ (कम से कम 2 एन्क्रिप्शन करने की सिफारिश की जाती है), और फाइल को सहेजें। एन्क्रिप्शन मोड में, फाइलें हेक्साडेसिमल .txt में सहेजी जाएंगी, डिक्रिप्शन मोड में, यह आपसे उस फाइल एक्सटेंशन के बारे में पूछेगा जिसे फाइल में होना चाहिए और अगले विंडो में इसे बाइनरी में सहेजेगा।
    
        # क्या किसी नए टेम्पलेट को किसी अन्य व्यक्ति के साथ साझा करना और सभी वर्णों की स्थिति को मेल करना जटिल है?
        नहीं, आपको केवल आकार (पंक्तियाँ/स्तंभ) प्रदान करने की आवश्यकता है और सभी वर्णों को एक कोमा द्वारा अलग करके साझा करें और टेम्पलेट सहेजें। डिफ़ॉल्ट टेम्पलेट का उपयोग करके एक एन्क्रिप्शन अनुक्रम के साथ, आप नए टेम्पलेट के वर्ण चिपका सकते हैं और उन्हें नया एन्क्रिप्टेड टेम्पलेट भेज सकते हैं।
    
        # मैं उस व्यक्ति के साथ नहीं मिल सकता जो मैंने बनाए गए टेम्पलेट में वर्णों की स्थिति को दिखाने के लिए, मैं क्या कर सकता हूँ?
        यदि आप व्यक्तिगत रूप से नहीं मिल सकते हैं, तो आपको मानों की अनुक्रम को साझा करने का तरीका ढूंढना होगा ताकि यदि एल्गोरिदम आपकी बातचीत की समीक्षा करता है, तो यह न देखे कि आप मान साझा कर रहे हैं। यदि इसके प्रति जागरूक हो, तो उसी माध्यम का उपयोग न करें बल्कि विभिन्न माध्यमों का उपयोग करें, और केवल आप दोनों ही समझने वाले निर्देशों के साथ मानों को इस तरह से बदलें कि एल्गोरिदम इसका संबंध मान न सके। डिफ़ॉल्ट टेम्पलेट का उपयोग करने के अलावा, एक बार जब आपके पास अनुक्रम हो, तो आप नए टेम्पलेट बना सकते हैं जो एन्क्रिप्टेड संदेशों में विवरण प्रदान करते हैं।
    
        # क्या आप और बदलाव जोड़ेंगे?
        हाँ, मैंने पासवर्ड मानों पर नियंत्रण जोड़ने और पासवर्ड के रूप में असाइन किए जा सकने वाले वर्णों को जोड़ने/संपादित करने के बारे में सोचा है। यदि आप अपने एन्क्रिप्शन में पासवर्ड सक्रिय करना चाहते हैं, तो विशेष वर्ण को टेक्स्ट में कॉपी और पेस्ट करें, भले ही आपकी भाषा उस वर्ण को प्रदान न करे।
        
        # क्या यह अधिक भाषाओं में अनुवादित होगा?
        हाँ, मैं इसे सभी के लिए सुलभ बनाने के लिए काम करता रहूंगा। डिस्कॉर्ड पर शामिल हों और अपनी भाषा की मांग करें। हालांकि, ईमानदारी से कहूं तो, LIVENCRYPT को आपकी भाषा में होने की आवश्यकता नहीं है; यह बहुत सहज है। यहां तक कि एक नया टेम्पलेट बनाते समय आपको नई वर्ण जोड़ने की अनुमति मिलती है जो उपलब्ध भाषाओं में नहीं दिखाई देती।
    
        # क्या एन्क्रिप्शन साझा करने के नए तरीके बनाए जाएंगे?
        हाँ, मैं वेब3 और P2P कनेक्शनों का उपयोग करके AI द्वारा बनाए गए आभासी परिदृश्यों में इंटरैक्शन की योजना बना रहा हूँ। परिदृश्य अद्वितीय होंगे और सत्र समाप्त होने के बाद हटा दिए जाएंगे।
        
        # इस ऐप्लिकेशन की क्या आवश्यकताएँ हैं?
        इसका उपयोग बिना इंटरनेट एक्सेस के किया जा सकता है और इसका उपयोग चाँद तक पहुंचने के लिए उपयोग की गई तकनीक के रूप में किया जा सकता है और यह पूरी तरह से काम करेगा। दुर्भाग्यवश, तकनीक गायब हो गई है और हम चाँद पर वापस नहीं जा सकते, लेकिन आप किसी भी डिवाइस पर LIVENCRYPT का उपयोग कर सकते हैं, चाहे वह कितना भी पुराना हो। यहां तक कि यदि आपके पास टेम्पलेट और अनुक्रम मान हैं, तो आप मैन्युअल रूप से एन्क्रिप्ट और डिक्रिप्ट कर सकते हैं।
    
        # क्या LIVENCRYPT का उपयोग एन्क्रिप्टेड फ़ोटो, वीडियो, ऑडियो भेजने के लिए किया जा सकता है?
        स्पष्ट रूप से अभी नहीं, लेकिन शायद भविष्य में कभी हो सकता है।
    
        # कोई विज्ञापन नहीं हैं और ऐप्लिकेशन मुफ्त है। धोखा कहां है?
        हमें यह विश्वास करने के लिए बनाया गया है कि यदि कुछ का कोई मूल्य नहीं है और किसी के पास हो सकता है, तो यह स्वयं के लिए बेकार है। हालांकि, हम "मुफ्त" प्लेटफार्मों का उपयोग करते हैं, और सिस्टम में कुछ भी मुफ्त नहीं है; हम में से प्रत्येक उनके लिए एक उत्पाद हैं और एल्गोरिदम हमारी सभी गतिविधियों को एकत्र करता है ताकि बाद में हमें हमारे हित या किसी भी चीज़ को विज्ञापन के माध्यम से बेचा जा सके। यदि आप मानवता के लिए एक अच्छा बनाना चाहते हैं, तो कोई बड़ी खुशी नहीं है कि हर मानव इसका उपयोग बिना किसी रुकावट के करे। इसलिए, मैं उन लोगों का आभारी रहूंगा जो ऐप्लिकेशन को साझा करते हैं, इसका उपयोग करते हैं और जो अपनी आभार व्यक्त करने के लिए दान करना चाहते हैं, मैं निम्नलिखित वॉलेट साझा करता हूँ: 
        एथेरियम 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71 
        धूपघड़ी FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        बीटीसी bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn 
        मोनेरो 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
        # GPLv3 लाइसेंस क्यों?
        पारदर्शिता के लिए, यह दिखाते हुए कि कोई बैकडोर या कुछ संदिग्ध नहीं है और ताकि कोई भी LIVENCRYPT को सुधारने में अपना योगदान दे सके।
    
        # मूल कोड कहाँ देखा जा सकता है?
        आप LIVENCRYPT 1.1 कोड को यहाँ पाएंगे: github.com/Synergia86 और gitee.com/Synergia_0ef4
    
        # क्या आप त्रुटियों की रिपोर्ट और विचार सुझाव देना चाहेंगे?
        हो सकता है कि आपको प्रोग्रामिंग की जानकारी न हो, लेकिन यदि आप सहयोग करना चाहते हैं, तो किसी भी त्रुटियों और विचारों को साझा करने के लिए डिस्कॉर्ड समुदाय में शामिल हों।
    
        # कोई भी असली प्रोग्रामर कोड को देखकर हंसेगा।
        मुझे आश्चर्य नहीं होगा, और कुछ शायद कोड का विश्लेषण करने के बाद अपने बाल खींच लेंगे। मैंने इसे ChatGPT और Claude.ai का उपयोग करके बनाया है। मुझे कहना होगा कि यह आसान नहीं था, हजारों परीक्षणों और त्रुटियों के दौरान बहुत धैर्य और perseverance के साथ। मैंने IT में प्रशिक्षण प्राप्त किया लेकिन प्रोग्रामिंग के क्षेत्र में नहीं, इसलिए संरचना का पालन न करने के लिए माफ करें। सबसे महत्वपूर्ण बात यह है कि यह काम करता है।
    
        # मेरे पास छिपाने के लिए कुछ भी नहीं है, मैं अधिकारियों द्वारा कहे गए आदेशों का पालन करने वाला एक अच्छा, आज्ञाकारी दास हूँ।
        एक दिन आप मानवता को धन्यवाद देंगे जिसने इस वास्तविकता को सभी के सामान्य लाभ के लिए बेहतर बनाने के लिए कदम उठाया। आप अपने पथ पर NPC की तरह चल सकते हैं या अपनी छाप छोड़ सकते हैं, और आप जानते हैं क्या? दोनों मार्ग समान रूप से मान्य हैं!
    
        # सिस्टम मुझे जांचेगा यदि मैं ऐप्लिकेशन का उपयोग करता हूँ।
        सिस्टम के पास हर मानव का जन्म से ही विस्तृत रिकॉर्ड है, और यदि हम कुछ नहीं करते हैं तो हम सांस लेने के लिए भी भुगतान करेंगे।
    
        # जो जीनियस मानवता के भले के लिए योगदान देते हैं, उनका मृत्यु-दंड के दुर्घटनाओं में अंत होता है। क्या आपको डर है कि आपके साथ कुछ हो सकता है?
        यदि मुझे डर होता, तो LIVENCRYPT कभी सामने नहीं आता। यहाँ हम अपनी छाप छोड़ने के लिए हैं, और अगर मुझे जाना पड़े, तो मैं अगले जीवन में लौटूंगा ताकि परेशानी जारी रहे। जितना अधिक डर वे हमें चाहते हैं, उतना ही हमें उनकी बनाई हुई शो से हंसना चाहिए। डर फैलाना और इसे मानना भी हमें मार देता है! हंसो और यात्रा का आनंद लो!
                """,                            
                "Français": """
        # À quoi sert LIVENCRYPT?
        LIVENCRYPT sert à maintenir des conversations 100% privées. Vous êtes maintenant le premier niveau de sécurité en créant un chiffrement du contenu et seul le destinataire connaîtra la fréquence pour déchiffrer le contenu.
    
        # Il n'y a pas de manuel pour utiliser LIVENCRYPT?
        Chiffrer le texte : le texte non chiffré sera chiffré.
        Déchiffrer le texte : le texte chiffré sera déchiffré.
        Dans Valeur : uniquement des chiffres de 0 à 1000.
        Sélectionnez le modèle contenant les caractères ajoutés dans le texte et cliquez sur exécuter pour voir le résultat.
        Mot de passe : Dans cette version, si vous ajoutez l'un des caractères spéciaux suivants au texte : ¢|@#~½¶←↓→ˀ|¢ª─¬, il vous sera demandé d'insérer un mot de passe lors de l'exécution. Vous devrez ajouter le caractère spécial du texte et les 7 caractères suivants (l'espace compte également comme un caractère). Exemple : Salut~1234567890 vous demandera d'insérer le mot de passe = ~1234567 et une fois validé, le texte sera chiffré. Avec le texte chiffré, pour utiliser la fonction de déchiffrement, vous devrez vous souvenir du mot de passe, dans ce cas pour que le déchiffrement s'exécute, vous devrez introduire ~1234567.
        Gérer les modèles : créer des modèles, en sélectionnant une langue, les caractères seront affichés pour les ajouter individuellement ou utiliser le bouton ajouter tout. Dans Numéros/signes, vous trouverez les chiffres et signes des langues. Le caractère spécial est l'espace "␣" pour qu'il soit exécuté dans le chiffrement. S'il n'est pas ajouté et que vous utilisez l'espace, il laissera des espaces dans le chiffrement.
        Sélectionner la taille : cela concerne les lignes et les colonnes que le modèle aura. Vous pouvez utiliser les valeurs par défaut ou ajouter les valeurs souhaitées, mais pour enregistrer le modèle, vous devrez laisser le compteur de caractères à zéro.
        Aléatoiriser : déplace aléatoirement les caractères ajoutés.
        Nettoyer : élimine tous les caractères ajoutés.
        Supprimer le dernier caractère.
        Enregistrer le modèle : indiquez le nom du modèle et enregistrez.
        Pour éditer, seules les modèles créés apparaîtront. Vous ne pourrez supprimer que les modèles que vous avez créés. Les modèles par défaut peuvent être consultés en regardant le code source.
        Sur la page principale, il y a une icône en haut à droite pour accéder aux paramètres. Vous pouvez changer la langue, modifier la taille de la police entre une valeur de 8 et 24. Questions fréquentes, conseils, crédits et licence.

        # Pour chiffrer ou déchiffrer un fichier. Sélectionnez la fonction à effectuer, chargez le fichier, insérez les valeurs, exécutez autant de fois que nécessaire (il est recommandé de réaliser au moins 2 chiffrages), et enregistrez le fichier. En mode chiffrement, les fichiers seront enregistrés en format hexadécimal .txt, en mode déchiffrement, il vous demandera l'extension du fichier à avoir, puis l'enregistrera en binaire dans la fenêtre suivante.
    
        # Est-il compliqué de partager un nouveau modèle avec une autre personne et que la position de tous les caractères corresponde?
        Non, vous devez simplement indiquer la taille (lignes/colonnes) et partager tous les caractères séparés par une virgule, puis enregistrer le modèle. En ayant une séquence de chiffrement en utilisant les modèles par défaut, vous pouvez coller les caractères du nouveau modèle et envoyer le nouveau modèle chiffré.
    
        # Je ne peux pas rencontrer la personne pour lui indiquer la position des caractères dans le modèle que j'ai créé, que puis-je faire?
        Si vous ne pouvez pas vous rencontrer en personne, vous devez trouver un moyen d'échanger la séquence de valeurs de manière à ce que si l'algorithme examine vos conversations, il ignore que vous partagez des valeurs et, si vous en êtes conscient, ne pas utiliser le même moyen, mais des moyens différents et avec des instructions que seuls vous deux comprendrez, en altérant les valeurs, mais l'algorithme ne pourra pas interpréter qu'il y a un lien avec les valeurs. De plus, utilisez les modèles par défaut et une fois que vous avez la séquence, vous pouvez créer de nouveaux modèles en fournissant des détails dans les messages chiffrés.
    
        # Apporterez-vous d'autres changements?
        Oui, j'ai pensé à ajouter un contrôle sur les valeurs du mot de passe et à pouvoir ajouter/modifier les caractères pouvant être attribués comme mot de passe. Copiez et collez un caractère spécial dans le texte si vous souhaitez activer le mot de passe dans votre chiffrement, même si votre langue ne vous facilite pas le caractère.
    
        # Sera-t-il traduit en plusieurs langues?
        Oui, je continuerai à travailler pour qu'il soit accessible à tous. Accédez à discord.gg/sDRawvyXhy et demandez votre langue. Bien que, pour être honnête, il n'est pas nécessaire que LIVENCRYPT soit dans votre langue, c'est très intuitif, même en créant un nouveau modèle, vous permet d'ajouter de nouveaux caractères qui ne sont pas dans les langues listées.
    
        # De nouvelles façons de partager le chiffrement seront-elles créées?
        Oui, j'ai en tête une interaction dans des scénarios virtuels créés par IA avec une option de conversation vocale utilisant web3 et des connexions P2P. Les scénarios seraient uniques et supprimés à la fin de la session.
    
        # Quels sont les exigences de l'application?
        Il peut être utilisé sans avoir accès à Internet et la technologie utilisée pour atteindre la lune pourrait fonctionner parfaitement, malheureusement la technologie a disparu et nous ne pouvons plus retourner sur la lune, mais vous pouvez utiliser LIVENCRYPT sur n'importe quel appareil, même s'il est très ancien. Même si vous avez le modèle et les valeurs des séquences, vous pouvez le chiffrer et le déchiffrer manuellement.
    
        # LIVENCRYPT peut-il être utilisé pour envoyer des photos, des vidéos et des fichiers audio cryptés?
        Évidemment pas maintenant, mais peut-être demain oui.
    
        # Il n'y a pas de publicités et l'application n'est pas payante, où est l'astuce?
        On nous a fait croire que si quelque chose n'a pas de valeur et peut être possédé par tout le monde, cela n'a aucune valeur pour soi. Cependant, nous utilisons des plateformes "gratuites" et dans le système, rien n'est gratuit, car chacun de nous est un produit pour eux et l'algorithme collecte toutes nos actions pour ensuite nous vendre nos intérêts ou tout ce que nous avons commenté via la publicité. Si vous voulez créer un bien pour l'Humanité, il n'y a pas de plus grande joie que TOUT ÊTRE HUMAIN l'utilise sans aucun obstacle. Je serai donc reconnaissant envers ceux qui partageront l'application, l'utiliseront et pour ceux qui veulent exprimer leur gratitude par des dons, je partage les portefeuilles suivants:
        ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
        Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
        # Pourquoi la licence GPLv3?
        Pour la transparence, démontrant qu'il n'y a pas de porte dérobée ni rien de suspect, et pour que chacun puisse apporter sa pierre à l'édifice pour améliorer LIVENCRYPT.
    
        # Où peut-on voir le code source?
        Le code LIVENCRYPT 1.1 se trouve sur : github.com/Synergia86 et gitee.com/Synergia_0ef4
    
        # J'aimerais signaler des bugs et suggérer des idées.
        Vous pouvez ne rien savoir en programmation, mais si vous voulez collaborer, accédez à la communauté discord.gg/sDRawvyXhy pour partager les bugs et les idées que vous avez en tête.
    
        # Tout programmeur digne de ce nom va se moquer du code.
        Cela ne me surprendrait pas du tout et certains vont même s'arracher les cheveux du pubis après avoir analysé tout le code. Je l'ai créé en utilisant chatgpt et claude.ai, je dois dire que cela n'a pas été facile, beaucoup de calme et de persévérance face à des milliers de tests et d'erreurs. J'ai étudié l'informatique mais pas en tant que programmeur, pardonnez-moi de ne pas respecter la structure. Le plus important, c'est que cela FONCTIONNE.
    
        # Je n'ai rien à cacher, je suis un bon esclave obéissant à ce que me disent les autorités.
        Un jour, vous serez reconnaissant à l'HUMANITÉ qui a décidé de faire le pas pour rendre cette réalité meilleure pour le bénéfice commun de tous. Vous pouvez suivre votre chemin comme un PNJ ou vous pouvez laisser votre empreinte et savez-vous ce qui est mieux? Que les deux chemins sont tout aussi valables!
    
        # Le système va m'enquêter si j'utilise l'application.
        Le système a un registre détaillé de chaque ÊTRE HUMAIN depuis sa naissance et si nous ne faisons rien, nous finirons par payer pour respirer.
    
        # Les génies qui ont contribué à un bien pour l'Humanité ont fini par avoir des accidents mortels, avez-vous peur qu'il puisse vous arriver quelque chose?
        Si j'avais peur, LIVENCRYPT n'aurait pas vu le jour. Nous sommes ici pour laisser notre empreinte et si je dois partir, je reviendrai dans une autre vie pour continuer à faire chier le monde. Plus ils veulent que nous ayons peur, plus nous devons rire du spectacle qu'ils nous créent. Inspirer la peur et y croire nous tue aussi ! Riez et profitez du chemin!
                """,
                "عربي": """
        # ما هو استخدام LIVENCRYPT؟
        LIVENCRYPT يُستخدم للحفاظ على المحادثات بنسبة ١٠٠٪ خصوصية. أنت الآن المستوى الأول من الأمان بإنشاء تشفير للمحتوى فقط المستقبل يعرف التردد لفك تشفير المحتوى.
    
        # هل هناك دليل لاستخدام LIVENCRYPT؟
        تشفير النص: النص غير المشفر سيتم تشفيره.
        فك تشفير النص: النص المشفر سيتم فك تشفيره.
        في القيمة: أرقام فقط من ٠ إلى ١٠٠٠.
        اختر النموذج الذي يحتوي على الأحرف المضافة في النص واضغط على تشغيل لرؤية النتيجة.
        كلمة المرور: في هذه النسخة إذا أضفت واحدًا من الأحرف الخاصة التالية إلى النص: ¢|@#~½¶←↓→ˀ|¢ª─¬، سيُطلب منك إدخال كلمة مرور عند التشغيل وسيتعين عليك إضافة الحرف الخاص من النص و٧ أحرف تالية (حتى المسافة تُعتبر كحرف). مثال: hola~١٢٣٤٥٦٧٨٩ سيُطلب منك إدخال كلمة مرور = ~١٢٣٤٥٦٧ وعند التحقق سيتم تشفير النص. مع النص المشفر عند استخدام وظيفة فك التشفير سيتعين عليك تذكر كلمة المرور، في هذه الحالة لكي يتم تنفيذ فك التشفير، سيتعين عليك إدخال ~١٢٣٤٥٦٧.
        إدارة النماذج: إنشاء النماذج، عند اختيار لغة ستعرض الأحرف لإضافتها بشكل فردي أو استخدام زر إضافة الكل. في الأرقام/الرموز ستجد الأرقام والرموز الخاصة باللغات. كحرف خاص يوجد المسافة "␣" لتنفيذها في التشفير، إذا لم تُضف واستخدمت المسافة ستترك مسافات في التشفير.
        تحديد الحجم: يتعلق بعدد الصفوف والأعمدة التي سيحتوي عليها النموذج. يمكنك استخدام القيم الافتراضية أو إضافة القيم التي ترغب بها ولكن لحفظ النموذج سيتعين عليك ترك عداد الأحرف على صفر.
        عشوائي: يحرك الأحرف المضافة بشكل عشوائي.
        تنظيف: يحذف جميع الأحرف المضافة.
        حذف آخر حرف.
        حفظ النموذج: أدخل اسم النموذج واحفظه.
        لتحرير، سيظهر فقط النماذج التي أنشأتها. لن تتمكن من حذف النماذج الافتراضية ولكن يمكنك رؤية النماذج الافتراضية من خلال الاطلاع على الشيفرة المصدرية.
        في الصفحة الرئيسية، هناك أيقونة في الزاوية العلوية اليمنى للوصول إلى الإعدادات. يمكنك تغيير اللغة، وتغيير حجم الخط بين قيمة ٨ و٢٤. الأسئلة الشائعة، النصائح، الائتمانات، والترخيص.

        # لتشفير أو فك تشفير ملف. اختر الوظيفة التي تريد تنفيذها، قم بتحميل الملف، أدخل القيم، نفّذ العملية عدة مرات حسب الحاجة (يُوصى بإجراء 2 تشفيرات على الأقل)، واحفظ الملف. في وضع التشفير، سيتم حفظ الملفات بتنسيق .txt في شكل سداسي عشري، وفي وضع فك التشفير سيطلب منك إدخال امتداد الملف المطلوب وفي النافذة التالية سيحفظه كملف ثنائي.
    
        # هل من الصعب مشاركة نموذج جديد مع شخص آخر بحيث يتطابق موقع جميع الأحرف؟
        لا، ما عليك سوى تحديد الحجم (الصفوف/الأعمدة) ومشاركة جميع الأحرف مفصولة بفاصلة ثم حفظ النموذج. باستخدام تسلسل التشفير باستخدام النماذج الافتراضية، يمكنك لصق الأحرف من النموذج الجديد وإرسال النموذج الجديد المشفر.
    
        # لا أستطيع مقابلة الشخص لتوضيح موضع الأحرف في النموذج الذي أنشأته، ماذا يمكنني أن أفعل؟
        إذا لم تتمكن من الاجتماع شخصيًا، يجب أن تجد طريقة لتبادل تسلسل القيم بطريقة تجعلها غير ملحوظة إذا قام الخوارزم بمراجعة محادثاتكم. إذا كنت على علم بذلك، فلا تستخدم نفس الوسيلة، بل وسائل مختلفة ومع تعليمات فقط أنتم الاثنان تفهمونها، بحيث تقوم بتغيير القيم ولكن الخوارزم لا يكون قادرًا على تفسير أن هناك علاقة بالقيم. بالإضافة إلى ذلك، استخدم النماذج الافتراضية وبمجرد أن يكون لديك التسلسل، يمكنك إنشاء نماذج جديدة بإعطاء تفاصيل في الرسائل المشفرة.
    
        # هل ستضيف تغييرات أخرى؟
        نعم، فكرت في إضافة تحكم على قيم كلمة المرور والقدرة على إضافة/تعديل الأحرف التي يمكن تعيينها ككلمة مرور. انسخ والصق حرفًا خاصًا في النص إذا كنت تريد تفعيل كلمة المرور في تشفيرك، حتى إذا كانت لغتك لا توفر الحرف.
    
        # هل سيتم ترجمته إلى لغات أخرى؟
        نعم، سأستمر في العمل لجعله متاحًا للجميع. انضم إلى الديسكورد واطلب لغتك. على الرغم من أن الصراحة، ليس من الضروري أن يكون LIVENCRYPT بلغتك، فهو سهل الفهم حتى عند إنشاء نموذج جديد، يمكنك إضافة أحرف جديدة غير موجودة في اللغات المدرجة.
    
        # هل سيتم إنشاء طرق جديدة لمشاركة التشفير؟
        نعم، أفكر في التفاعل في سيناريوهات افتراضية تم إنشاؤها بواسطة الذكاء الاصطناعي مع خيار المحادثة الصوتية باستخدام web3 واتصالات P2P. ستكون السيناريوهات فريدة وسيتم حذفها بعد انتهاء الجلسة.
    
        # ما هي متطلبات التطبيق؟
        يمكن استخدامه دون الحاجة إلى اتصال بالإنترنت، وكانت التكنولوجيا المستخدمة للوصول إلى القمر ستعمل بشكل مثالي، ولكن للأسف فقدت التكنولوجيا ولم نعد قادرين على العودة إلى القمر، ولكن يمكنك استخدام LIVENCRYPT على أي جهاز حتى لو كان قديمًا جدًا. حتى إذا كان لديك النموذج وقيم التسلسل، يمكنك تشفيره وفكه يدويًا.
    
        # هل يمكن استخدام LIVENCRYPT لإرسال الصور، والفيديوهات، والملفات الصوتية، ...؟
        بالطبع لا الآن، لكن ربما في المستقبل.
    
        # هل يمكن استخدام LIVENCRYPT لإرسال الصور ومقاطع الفيديو والصوت المشفرة؟
        لقد تم إيهامنا بأنه إذا لم يكن هناك قيمة لشيء ويمكن أن يمتلكه أي شخص، فلا قيمة له بالنسبة لنا. ومع ذلك، نحن نستخدم منصات "مجانًا" وفي النظام، لا يوجد شيء مجاني، لأن كل واحد منا هو منتج لهم والخوارزم يجمع جميع أفعالنا لبيع اهتماماتنا أو أي شيء قمنا بالتحدث عنه عبر الإعلانات. إذا كنت تريد إنشاء خير للبشرية، لا يوجد فرح أعظم من أن يستخدم كل إنسان كل شيء بدون أي قيود. لذلك، سأكون ممتنًا لأولئك الذين يشاركون التطبيق، ويستخدمونه ولأولئك الذين يريدون تقديم شكرهم بالتبرعات، أشارك المحفظات التالية: 
        
     0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71  سولانا 
    FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn  إيثريوم   
    bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn   بيتكوين
    47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g  مونيرو
    
    
        # لماذا ترخيص GPLv3؟
        من أجل الشفافية، لإثبات عدم وجود أبواب خلفية أو أي شيء مشبوه، ولتمكين أي شخص من المساهمة في تحسين LIVENCRYPT.
    
        # أين يمكن رؤية الشيفرة الأصلية؟
        يمكنك العثور على الشيفرة LIVENCRYPT 1.1 في: github.com/Synergia86 و gitee.com/Synergia_0ef4
    
        # أود الإبلاغ عن الأخطاء وتقديم الأفكار.
        يمكنك عدم معرفة البرمجة، ولكن إذا كنت تريد المساهمة، انضم إلى مجتمع الديسكورد لمشاركة الأخطاء والأفكار التي لديك في ذهنك.
    
        # أي مبرمج حقيقي سيضحك من الشيفرة.
        لن أتفاجأ على الإطلاق، وبعضهم قد يمزق شعره بعد تحليل الشيفرة. لقد أنشأتها باستخدام chatgpt وclaude.ai، يجب أن أقول أنه لم يكن سهلاً، الكثير من الهدوء والمثابرة بعد آلاف التجارب والأخطاء. درست الكمبيوتر ولكن ليس كمبرمج، اعذرني لعدم احترام الهيكل. الأهم من ذلك، أنه يعمل.
    
        # ليس لدي شيء لأخفيه، أنا عبد جيد أطيع ما تقوله السلطات.
        يومًا ما ستشكر الإنسانية التي قررت أن تأخذ الخطوة لجعل هذه الحقيقة أفضل من أجل المصلحة المشتركة للجميع. يمكنك اتباع طريقك كـ NPC أو يمكنك ترك بصمتك، وأنت تعرف ما هو الأفضل؟ أن كلا الطريقين لهما نفس القيمة!
    
        # سيفحصني النظام إذا استخدمت التطبيق.
        لدى النظام سجل مفصل لكل إنسان منذ ولادته وإذا لم نفعل شيئًا، سينتهي بنا الأمر بدفع ثمن التنفس.
    
        # العباقرة الذين ساهموا في خير البشرية انتهوا بالحوادث القاتلة، هل تخاف من أن يحدث لك شيء؟
        إذا كنت خائفًا، لما كان LIVENCRYPT قد خرج إلى النور. نحن هنا لترك بصمتنا وإذا كان علي الرحيل، سأعود في حياة أخرى للاستمرار في إزعاج العالم. كلما زاد خوفهم، كلما زاد علينا الضحك من العرض الذي يخلقونه لنا. نشر الخوف والإيمان به يقتلنا أيضًا! اضحك واستمتع بالطريق!
                """,
                "বাংলা": """
        # LIVENCRYPT কি জন্য ব্যবহৃত হয়?
        LIVENCRYPT ব্যবহার করা হয় ১০০% গোপনীয় চ্যাটের জন্য। এখন আপনি সুরক্ষার প্রথম স্তর হিসেবে কন্টেন্ট এনক্রিপ্ট করবেন এবং শুধুমাত্র প্রাপক ডিসক্রিপশন ফ্রিকোয়েন্সি জানবে।
    
        # LIVENCRYPT ব্যবহার করার কোন ম্যানুয়াল নেই?
        টেক্সট এনক্রিপ্ট করুন: অপরিবর্তিত টেক্সট এনক্রিপ্ট হবে।
        টেক্সট ডিসক্রিপ্ট করুন: এনক্রিপ্ট করা টেক্সট ডিসক্রিপ্ট হবে।
        মানে: শুধুমাত্র সংখ্যা ০ থেকে ১০০০ পর্যন্ত।
        সেই টেমপ্লেট নির্বাচন করুন যাতে টেক্সটের সাথে যুক্ত অক্ষরগুলি রয়েছে এবং রান বাটনে ক্লিক করুন ফলাফল দেখার জন্য।
        পাসওয়ার্ড: এই সংস্করণে যদি টেক্সটে নিম্নলিখিত বিশেষ অক্ষরগুলির একটি যোগ করেন: ¢|@#~½¶←↓→ˀ|¢ª─¬, এটি চালানোর সময় আপনাকে পাসওয়ার্ড প্রবেশ করতে বলবে এবং আপনাকে টেক্সটের বিশেষ অক্ষর এবং পরবর্তী ৭টি অক্ষর (স্পেসও একটি অক্ষর হিসাবে গণ্য হয়) যোগ করতে হবে। উদাহরণ: হ্যালো~১২৩৪৫৬৭৮৯০ আপনাকে পাসওয়ার্ড প্রবেশ করতে বলবে = ~১২৩৪৫৬৭ এবং যখন এটি যাচাই করা হবে টেক্সট এনক্রিপ্ট হবে। এনক্রিপ্ট করা টেক্সট ডিসক্রিপ্ট করতে হলে, আপনাকে পাসওয়ার্ড মনে রাখতে হবে, এই ক্ষেত্রে ডিসক্রিপ্ট করার জন্য আপনাকে ~১২৩৪৫৬৭ প্রবেশ করতে হবে।
        টেমপ্লেট পরিচালনা করুন: টেমপ্লেট তৈরি করুন, একটি ভাষা নির্বাচন করলে অক্ষরগুলি দেখাবে যা আপনি আলাদাভাবে যোগ করতে পারেন বা সবগুলি যোগ করার বোতাম ব্যবহার করতে পারেন। সংখ্যার/চিহ্নের মধ্যে আপনি ভাষার সংখ্যা এবং চিহ্নগুলি পাবেন। বিশেষ অক্ষর হিসাবে স্পেস "␣" রয়েছে যা এনক্রিপশনে প্রয়োগ করা যেতে পারে, যদি এটি যোগ না করা হয় এবং আপনি স্পেস ব্যবহার করেন, এটি এনক্রিপশনে স্পেস ছেড়ে দেবে।
        আকার নির্বাচন করুন: এটি টেমপ্লেটের সারি এবং কলামগুলির সম্পর্কে। আপনি ডিফল্ট মানগুলি ব্যবহার করতে পারেন বা আপনি যে মানগুলি চান তা যোগ করতে পারেন তবে টেমপ্লেট সংরক্ষণ করার জন্য আপনাকে অক্ষর কাউন্টারকে শূন্যে রাখতে হবে।
        এলোমেলো করুন: যোগ করা অক্ষরগুলি এলোমেলোভাবে সরান।
        পরিষ্কার করুন: যোগ করা সমস্ত অক্ষর মুছুন।
        শেষ অক্ষর মুছুন।
        টেমপ্লেট সংরক্ষণ করুন: টেমপ্লেটের নাম প্রবেশ করান এবং সংরক্ষণ করুন।
        সম্পাদনা করতে, শুধুমাত্র তৈরি করা টেমপ্লেটগুলি প্রদর্শিত হবে। শুধুমাত্র আপনি তৈরি করা টেমপ্লেটগুলি মুছতে পারবেন। ডিফল্ট টেমপ্লেটগুলি আপনি কেবল সোর্স কোড দেখে দেখতে পারবেন।
        মূল স্ক্রিনে, ডান উপরের কোণায় একটি আইকন রয়েছে সেটিংসে অ্যাক্সেস করতে। আপনি ভাষা পরিবর্তন করতে পারেন, ৮ থেকে ২৪ মানের মধ্যে ফন্টের আকার পরিবর্তন করতে পারেন। প্রায়শই জিজ্ঞাসিত প্রশ্নাবলী, পরামর্শ, ক্রেডিট এবং লাইসেন্স।

        # একটি ফাইল এনক্রিপ্ট বা ডিক্রিপ্ট করতে। সম্পাদন করার জন্য ফাংশনটি নির্বাচন করুন, ফাইলটি লোড করুন, মানগুলি প্রবেশ করান, যতবার প্রয়োজন রান করুন (ন্যূনতম ২ বার এনক্রিপশন করা সুপারিশ করা হয়), এবং ফাইলটি সংরক্ষণ করুন। এনক্রিপশন মোডে, ফাইলগুলি হেক্সাডেসিমাল .txt আকারে সংরক্ষণ করা হবে, ডিক্রিপশন মোডে এটি ফাইলের এক্সটেনশন সম্পর্কে আপনাকে জিজ্ঞাসা করবে এবং পরবর্তী উইন্ডোতে এটি বাইনারি আকারে সংরক্ষণ করবে।
   
        # নতুন টেমপ্লেট কারো সাথে শেয়ার করা এবং সমস্ত অক্ষরের অবস্থান মিলানো কি কঠিন?
        না, আপনাকে শুধু আকার (সারি/কলাম) উল্লেখ করতে হবে এবং সমস্ত অক্ষর কমা দ্বারা পৃথকভাবে শেয়ার করতে হবে এবং টেমপ্লেট সংরক্ষণ করতে হবে। ডিফল্ট টেমপ্লেট ব্যবহার করে এনক্রিপশন সিকোয়েন্স দিয়ে আপনি নতুন টেমপ্লেটের অক্ষরগুলি পেস্ট করতে পারেন এবং নতুন এনক্রিপ্ট করা টেমপ্লেট পাঠাতে পারেন।
    
        # আমি সেই ব্যক্তির সাথে দেখা করতে পারছি না যে টেমপ্লেটে অক্ষরগুলি কোথায় রাখতে হবে তা জানাতে, আমি কী করতে পারি?
        যদি আপনি ব্যক্তিগতভাবে মিলিত হতে না পারেন, আপনাকে কৌশল বের করতে হবে মানগুলির সিকোয়েন্স বিনিময় করার জন্য এমনভাবে যে আলগোরিদম যদি আপনার কথোপকথনগুলি দেখে, এটি বুঝতে পারবে না যে আপনি মানগুলি শেয়ার করছেন। এবং যদি আপনি এটি সচেতন হন, তবে একই মাধ্যম ব্যবহার করবেন না, বরং বিভিন্ন মাধ্যম এবং এমন নির্দেশাবলী যা কেবল আপনি এবং প্রাপক বুঝতে পারবেন, যা মানগুলি পরিবর্তন করবে কিন্তু আলগোরিদম এটি সম্পর্কিত হিসাবে ব্যাখ্যা করতে সক্ষম হবে না। ডিফল্ট টেমপ্লেটগুলি ব্যবহার করুন এবং সিকোয়েন্সটি থাকলে, এনক্রিপ্ট করা বার্তায় বিবরণ দেওয়ার মাধ্যমে নতুন টেমপ্লেট তৈরি করতে পারেন।
    
        # আপনি কি আরো পরিবর্তন আনবেন?
        হ্যাঁ, আমি পাসওয়ার্ডের মানগুলির উপর একটি নিয়ন্ত্রণ যোগ করার কথা ভাবছি এবং পাসওয়ার্ড হিসাবে নির্ধারণ করা যেতে পারে এমন অক্ষরগুলি যোগ/সম্পাদনা করার ক্ষমতা। যদি আপনার ভাষা বিশেষ অক্ষর সরবরাহ না করে তবে আপনার এনক্রিপশনে পাসওয়ার্ড সক্রিয় করতে একটি বিশেষ অক্ষর কপি এবং পেস্ট করুন।
    
        # এটি কি আরও ভাষায় অনুবাদ করা হবে?
        হ্যাঁ, আমি এটি সবার জন্য অ্যাক্সেসযোগ্য করার জন্য কাজ চালিয়ে যাব। ডিসকোর্ডে যোগ দিন এবং আপনার ভাষা অনুরোধ করুন। যদিও সৎভাবে বলছি, LIVENCRYPT আপনার ভাষায় হওয়া প্রয়োজন নেই, এটি খুবই স্বজ্ঞাত, এমনকি নতুন টেমপ্লেট তৈরি করলেও আপনি তালিকাভুক্ত ভাষাগুলিতে না থাকা নতুন অক্ষর যোগ করতে পারেন।
    
        # এনক্রিপশন শেয়ার করার নতুন পদ্ধতি তৈরি করা হবে কি?
        হ্যাঁ, আমি AI দ্বারা তৈরি ভার্চুয়াল দৃশ্যে কণ্ঠ কথোপকথনের বিকল্প সহ ওয়েব৩ এবং P2P সংযোগ ব্যবহার করে ইন্টারঅ্যাকশন ভাবছি। দৃশ্যগুলি অনন্য হবে এবং সেশনের শেষে মুছে ফেলা হবে।
    
        # অ্যাপ্লিকেশনের জন্য কি প্রয়োজনীয়তা আছে?
        এটি ইন্টারনেট ছাড়াই ব্যবহার করা যেতে পারে এবং চাঁদে যাওয়ার জন্য ব্যবহৃত প্রযুক্তি ব্যবহৃত হলেও এটি নিখুঁতভাবে কাজ করবে, তবে দুর্ভাগ্যবশত প্রযুক্তিটি হারিয়ে গেছে এবং আমরা আর চাঁদে ফিরতে পারি না, তবে আপনি যেকোনো ডিভাইসে LIVENCRYPT ব্যবহার করতে পারবেন, যতই পুরানো হোক না কেন। এমনকি যদি আপনার টেমপ্লেট এবং সিকোয়েন্সের মান থাকে তবে আপনি এটি ম্যানুয়ালি এনক্রিপ্ট এবং ডিসক্রিপ্ট করতে পারেন।
    
        # এনক্রিপ্ট করা ছবি, ভিডিও, অডিও পাঠাতে LIVENCRYPT ব্যবহার করা যেতে পারে?
        অবশ্যই এখন নয়, তবে হয়তো ভবিষ্যতে।
    
        # বিজ্ঞাপন নেই এবং অ্যাপ্লিকেশনটি বিনামূল্যে, কোন কৌশল আছে?
        আমাদের বিশ্বাস করা হয়েছে যে যদি কোন কিছুর মূল্য না থাকে এবং যে কেউ তা পেতে পারে, তবে এটি আমাদের জন্য কোন মূল্য নেই। তবুও আমরা "বিনামূল্যে" প্ল্যাটফর্মগুলি ব্যবহার করি এবং সিস্টেমে কিছুই বিনামূল্যে নয়, কারণ আমরা প্রত্যেকে তাদের জন্য একটি পণ্য এবং আলগোরিদম আমাদের সমস্ত ক্রিয়াকলাপ সংগ্রহ করে আমাদের আগ্রহগুলি বা আমরা যে কোনো কিছু আলোচনা করেছি তার বিজ্ঞাপন হিসাবে বিক্রি করার জন্য। যদি আপনি মানবতার জন্য একটি ভাল কিছু তৈরি করতে চান, তাহলে প্রত্যেক মানুষের দ্বারা ব্যবহার করা একটি বড় আনন্দ। অতএব, যারা অ্যাপ্লিকেশনটি শেয়ার করেন, ব্যবহার করেন এবং যারা তাদের কৃতজ্ঞতা প্রদানের জন্য দান করতে চান তাদের জন্য আমি নিম্নলিখিত ওয়ালেট শেয়ার করছি: 
        ইথেরিয়াম 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
        সোলানা FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        বিটকয়েন bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        মোনেরো 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
        # কেন GPLv3 লাইসেন্স?
        স্বচ্ছতার জন্য, পিছনের দরজা বা সন্দেহজনক কিছু নেই তা প্রমাণ করার জন্য এবং LIVENCRYPT উন্নতিতে যেকেউ অবদান রাখতে সক্ষম হওয়ার জন্য।
    
        # মূল কোড কোথায় দেখা যাবে?
        আপনি LIVENCRYPT 1.1 এর কোড খুঁজে পাবেন: github.com/Synergia86 এবং gitee.com/Synergia_0ef4
    
        # আমি ত্রুটি রিপোর্ট এবং আইডিয়া প্রস্তাব করতে চাই।
        আপনি প্রোগ্রামিং সম্পর্কে কিছুই না জানলেও আপনি যদি অবদান রাখতে চান, ত্রুটি এবং আপনার মাথায় থাকা আইডিয়া শেয়ার করতে কমিউনিটি ডিসকোর্ডে যোগ দিন।
    
        # যেকোনো প্রকৃত প্রোগ্রামার কোডটি দেখে হাসবে।
        আমি মোটেই অবাক হব না এবং কিছু হয়তো কোড বিশ্লেষণ করার পরে তাদের চুল ছিঁড়বে। আমি এটি chatgpt এবং claude.ai ব্যবহার করে তৈরি করেছি, আমাকে বলতে হবে এটি সহজ ছিল না, হাজারো চেষ্টা ও ভুলের পরে অনেক শান্তি এবং ধৈর্যের প্রয়োজন। আমি কম্পিউটার পড়েছি কিন্তু প্রোগ্রামার হিসেবে নয়, স্ট্রাকচার সম্মান না করার জন্য ক্ষমাপ্রার্থী। সবচেয়ে গুরুত্বপূর্ণ, এটি কাজ করে।
    
        # আমার লুকানোর কিছু নেই, আমি একজন ভালো দাস যিনি কর্তৃপক্ষ যা বলে তাই পালন করি।
        একদিন আপনি সেই মানবতাকে ধন্যবাদ জানাবেন যিনি সবার জন্য মঙ্গল করার জন্য এই পদক্ষেপ নিয়েছেন। আপনি NPC হিসাবে আপনার পথ অনুসরণ করতে পারেন বা আপনি আপনার চিহ্ন রেখে যেতে পারেন এবং আপনি কি জানেন সবচেয়ে ভাল কি? উভয় পথের একই মূল্য!
    
        # যদি আমি অ্যাপ্লিকেশনটি ব্যবহার করি সিস্টেম আমাকে পরীক্ষা করবে।
        সিস্টেমের জন্ম থেকে প্রত্যেক মানুষের বিস্তারিত রেকর্ড রয়েছে এবং আমরা যদি কিছু না করি তবে শ্বাস নেওয়ার জন্যও আমাদের মূল্য দিতে হবে।
    
        # যারা মানবতার জন্য ভালো কিছু করেছেন তাদের মারাত্মক দুর্ঘটনা ঘটেছে, আপনি কি কিছু ঘটার ভয়ে আছেন?
        যদি আমি ভীত হতাম, LIVENCRYPT কখনও আলো দেখতে পেত না। আমরা এখানে আমাদের চিহ্ন রাখতে এসেছি এবং আমাকে যদি যেতে হয়, আমি বিশ্বকে বিরক্ত করতে অন্য জীবনে ফিরে আসব। যত বেশি তারা ভয় পায়, তত বেশি আমাদের তাদের তৈরি শো দেখে হাসা উচিত। ভয় ছড়ানো এবং তাতে বিশ্বাস করা আমাদেরও মেরে ফেলে! হাসুন এবং যাত্রার আনন্দ নি!
                """,
                "Русский": """
        # Для чего используется LIVENCRYPT?
        LIVENCRYPT используется для ведения 100% приватных бесед. Теперь вы являетесь первым уровнем безопасности, создавая шифрование контента, и только получатель будет знать частоту для расшифровки контента.
    
        # Нет руководства по использованию LIVENCRYPT?
        Зашифровать текст: нешифрованный текст станет зашифрованным.
        Расшифровать текст: зашифрованный текст станет расшифрованным.
        В значении: только числа от 0 до 1000.
        Выберите шаблон, содержащий добавленные символы в тексте, и нажмите "Выполнить", чтобы увидеть результат.
        Пароль: в этой версии, если в тексте добавлен один из следующих специальных символов: ¢|@#~½¶←↓→ˀ|¢ª─¬, при выполнении запроса вставьте пароль и добавьте специальный символ из текста и следующие 7 символов (пробел также считается символом). Пример: привет~1234567890 запросит ввести пароль = ~1234567 и при проверке текст будет зашифрован. Для расшифровки зашифрованного текста необходимо помнить пароль, в этом случае для выполнения расшифровки необходимо ввести ~1234567.
        Управление шаблонами: создание шаблонов, при выборе языка будут показаны символы для добавления их по одному или использовать кнопку "Добавить все". В "Числах/знаках" вы найдете числа и знаки для языков. Специальным символом является пробел "␣", который будет применен при шифровании, если он не добавлен, и вы используете пробел, он оставит пробелы в шифровании.
        Выбор размера: это количество строк и столбцов в шаблоне. Вы можете использовать значения по умолчанию или добавить желаемые значения, но для сохранения шаблона нужно установить счетчик символов на ноль.
        Перемешать: перемещает добавленные символы случайным образом.
        Очистить: удаляет все добавленные символы.
        Удалить последний символ.
        Сохранить шаблон: укажите имя шаблона и сохраните.
        Для редактирования будут показаны только созданные вами шаблоны. Вы можете удалить только созданные вами шаблоны. Шаблоны по умолчанию можно просмотреть в исходном коде.
        В главном окне в правом верхнем углу есть значок для доступа к настройкам. Вы можете изменить язык, изменить размер шрифта от 8 до 24. Часто задаваемые вопросы, советы, кредиты и лицензия.

        # Для шифрования или расшифровки файла. Выберите функцию для выполнения, загрузите файл, введите значения, выполните столько раз, сколько необходимо (рекомендуется выполнить минимум 2 шифрования), и сохраните файл. В режиме шифрования файлы будут сохранены в шестнадцатеричном формате .txt, в режиме расшифровки вам будет предложено указать расширение файла, а на следующем шаге файл будет сохранен в бинарном виде.
    
        # Трудно ли делиться новым шаблоном с другим человеком и совпадать ли положение всех символов?
        Нет, просто укажите размер (строки/столбцы) и поделитесь всеми символами, разделенными запятыми, и сохраните шаблон. Используя последовательность шифрования с шаблонами по умолчанию, вы можете вставить символы нового шаблона и отправить зашифрованный новый шаблон.
    
        # Я не могу встретиться с человеком, чтобы указать ему размещение символов в созданном мной шаблоне. Что мне делать?
        Если вы не можете встретиться лично, вам придется придумать способ обмена последовательностью значений так, чтобы алгоритм, анализируя ваши беседы, не понял, что вы обмениваетесь значениями, и если он это поймет, не использовать одно и то же средство, а разные и с инструкциями, которые понимаете только вы и получатель, изменяющими значения, но алгоритм не сможет понять, что они связаны с этими значениями. Кроме того, используйте шаблоны по умолчанию, и как только у вас будет последовательность, вы можете создать новые шаблоны, давая подробности в зашифрованных сообщениях.
    
        # Хотите добавить еще изменения?
        Да, я подумал добавить контроль над значениями пароля и возможность добавления/редактирования символов, которые можно назначить паролем. Копируйте и вставляйте специальный символ в текст, если хотите активировать пароль в вашем шифровании, даже если ваш язык не предоставляет символ.
    
        # Будет ли переведено на другие языки?
        Да, я продолжу работать над тем, чтобы сделать его доступным для всех. Присоединяйтесь к discord.gg/sDRawvyXhy и запросите ваш язык. Хотя, честно говоря, LIVENCRYPT не обязательно должен быть на вашем языке, он очень интуитивно понятен, даже при создании нового шаблона вы можете добавлять новые символы, которых нет в указанных языках.
    
        # Будут ли созданы новые способы обмена шифрованием?
        Да, я думаю об интеракции в виртуальных сценах, созданных AI, с опцией голосового общения, используя web3 и P2P-соединения. Сцены будут уникальными и удаляться по завершении сеанса.
    
        # Какие требования к приложению?
        Его можно использовать без доступа к Интернету, и можно использовать технологию, которую использовали для полета на Луну, и она будет работать идеально, к сожалению, технология исчезла, и мы больше не можем вернуться на Луну, но вы можете использовать LIVENCRYPT на любом устройстве, каким бы старым оно ни было. Даже если у вас есть шаблон и значения последовательностей, вы можете зашифровать и расшифровать вручную.
    
        # Можно ли использовать LIVENCRYPT для отправки зашифрованных фотографий, видео и аудио?
        Конечно, сейчас нет, но, возможно, в будущем.
    
        # Нет рекламы и приложение бесплатно. Где подвох?
        Нас заставили верить, что если что-то не имеет ценности и это может иметь каждый, то для нас это не имеет значения. Однако мы используем "бесплатные" платформы, и в системе нет ничего бесплатного, так как каждый из нас является продуктом для них, и алгоритм собирает все наши действия, чтобы затем продавать нам наши интересы или что-то, что мы обсуждали, посредством рекламы. Если вы хотите создать благо для человечества, нет большей радости, чем чтобы КАЖДЫЙ ЧЕЛОВЕК использовал его без препятствий. Поэтому я буду благодарен тем, кто поделится приложением, использует его, и тем, кто хочет выразить свою благодарность пожертвованиями, делюсь следующими кошельками: 
        Эфириум 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
        Солана FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        Биткойн bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        Эфириум 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
        # Почему лицензия GPLv3?
        Для прозрачности, чтобы доказать, что нет задних дверей или чего-то подозрительного, и чтобы каждый мог внести свой вклад в улучшение LIVENCRYPT.
    
        # Где можно посмотреть оригинальный код?
        Вы найдете код LIVENCRYPT 1.1 на: github.com/Synergia86 и gitee.com/Synergia_0ef4
    
        # Хочу сообщить об ошибках и предложить идеи.
        Вы можете ничего не знать о программировании, но если хотите внести вклад, присоединяйтесь к сообществу discord.gg/sDRawvyXhy, чтобы делиться ошибками и идеями, которые у вас есть.
    
        # Любой настоящий программист будет смеяться над этим кодом.
        Я вовсе не удивлюсь, и некоторые даже будут рвать волосы после анализа всего кода. Я создал его с помощью chatgpt и claude.ai, должен сказать, что это было нелегко, много спокойствия и настойчивости при тысячах проб и ошибок. Я изучал информатику, но не в программировании, прошу прощения за нарушение структуры. Самое главное, это РАБОТАЕТ.
    
        # Мне нечего скрывать, я хороший раб, послушный властям.
        Однажды вы поблагодарите ЧЕЛОВЕЧЕСТВО, которое решило сделать этот шаг для общего блага всех. Вы можете идти по своему пути как NPC или оставить свой след, и знаете, что самое лучшее? Оба пути одинаково ценны!
    
        # Система будет следить за мной, если я использую приложение.
        У системы есть подробная запись о каждом ЧЕЛОВЕКЕ с рождения, и если мы ничего не сделаем, мы в конечном итоге будем платить за дыхание.
    
        # Гении, которые внесли вклад в благо человечества, заканчивались смертельными несчастными случаями. Вы боитесь, что с вами может что-то случиться?
        Если бы я боялся, LIVENCRYPT никогда бы не увидел свет. Мы здесь, чтобы оставить свой след, и если мне придется уйти, я вернусь в другой жизни, чтобы продолжать раздражать. Чем больше они хотят, чтобы мы боялись, тем больше мы должны смеяться над шоу, которое они создают. Внушение страха и вера в это тоже убивает нас! Смейтесь и наслаждайтесь путем!
        """,
                "Português": """
        # Para que serve o LIVENCRYPT?
        LIVENCRYPT serve para manter conversas 100% privadas. Agora você é o primeiro nível de segurança, criando uma criptografia do conteúdo, e apenas o destinatário saberá a frequência para descriptografar o conteúdo.
    
        # Não há um manual para usar o LIVENCRYPT?
        Criptografar texto: o texto não criptografado será criptografado.
        Descriptografar texto: o texto criptografado será descriptografado.
        No valor: apenas números de 0 a 1000.
        Selecione o modelo que contém os caracteres adicionados no texto e clique em executar para ver o resultado.
        Senha: nesta versão, se no texto você adicionar um dos seguintes caracteres especiais: ¢|@#~½¶←↓→ˀ|¢ª─¬, ele solicitará a inserção de uma senha ao executar e você deverá adicionar o caractere especial do texto e os 7 caracteres seguintes (o espaço também conta como caractere). Exemplo: ola~1234567890 solicitará a inserção da senha = ~1234567 e ao validar, o texto será criptografado. Para descriptografar o texto criptografado, você precisará lembrar a senha, neste caso, para que a descriptografia seja executada, você deverá inserir ~1234567.
        Gerenciar modelos: criar modelos, ao selecionar um idioma, serão exibidos os caracteres para adicioná-los individualmente ou usar o botão adicionar todos. Em Números/símbolos você encontrará os números e sinais dos idiomas. Como caractere especial, existe o espaço "␣" que será executado na criptografia, se não for adicionado e você usar o espaço, deixará espaços na criptografia.
        Selecionar tamanho: refere-se às linhas e colunas que o modelo terá. Você pode usar os valores padrão ou adicionar os valores desejados, mas para salvar o modelo, você deve deixar o contador de caracteres em zero.
        Aleatorizar: move aleatoriamente os caracteres adicionados.
        Limpar: Remove todos os caracteres adicionados.
        Apagar o último caractere.
        Salvar modelo: indique o nome do modelo e salve.
        Para editar, apenas os modelos criados serão exibidos. Você poderá excluir apenas os modelos que criou. Os modelos padrão podem ser visualizados no código-fonte.
        Na tela principal, há um ícone no canto superior direito para acessar as configurações. Você pode mudar o idioma, alterar o tamanho da fonte entre um valor de 8 e 24. Perguntas frequentes, dicas, créditos e licença.

        # Para criptografar ou descriptografar um arquivo. Selecione a função a ser realizada, carregue o arquivo, insira os valores, execute quantas vezes for necessário (recomendado fazer pelo menos 2 criptografias), e salve o arquivo. No modo de criptografia, os arquivos serão salvos em hexadecimal .txt, no modo de descriptografia, ele solicitará a extensão do arquivo e na próxima janela ele será salvo em binário.
    
        # É complicado compartilhar um novo modelo com outra pessoa e fazer coincidir a posição de todos os caracteres?
        Não, você só precisa indicar o tamanho (linhas/colunas) e compartilhar todos os caracteres separados por uma vírgula e salvar o modelo. Usando uma sequência de criptografia com os modelos padrão, você pode colar os caracteres do novo modelo e enviar o novo modelo criptografado.
    
        # Não posso encontrar a pessoa para indicar a colocação dos caracteres no modelo que criei. O que posso fazer?
        Se vocês não puderem se encontrar pessoalmente, terão que inventar uma maneira de trocar a sequência de valores de forma que, se o algoritmo examinar suas conversas, não perceba que vocês estão compartilhando valores e, se perceber, não usar o mesmo meio, mas meios diferentes e com instruções que apenas ambos entenderão, alterando os valores, mas o algoritmo não será capaz de interpretar que está relacionado aos valores. Além de usar os modelos padrão, uma vez que vocês tenham a sequência, podem criar novos modelos fornecendo detalhes nas mensagens criptografadas.
    
        # Você faria mais mudanças?
        Sim, pensei em adicionar um controle sobre os valores da senha e poder adicionar/editar os caracteres que podem ser atribuídos como senha. Copie e cole um caractere especial no texto se quiser ativar a senha na sua criptografia, mesmo que seu idioma não forneça o caractere.
    
        # Estará traduzido em mais idiomas?
        Sim, continuarei trabalhando para torná-lo acessível a todos. Acesse o discord.gg/sDRawvyXhy e solicite seu idioma. Embora, para ser sincero, o LIVENCRYPT não precisa estar no seu idioma, é muito intuitivo, até mesmo criando um novo modelo, você pode adicionar novos caracteres que não estão nos idiomas listados.
    
        # Serão criadas novas formas de compartilhar a criptografia?
        Sim, estou pensando em interação em cenários virtuais criados por IA com opção de conversa por voz usando web3 e conexões P2P. Os cenários seriam únicos e eliminados ao final da sessão.
    
        # Quais são os requisitos para o aplicativo?
        Pode ser usado sem acesso à Internet e poderia usar a tecnologia que foi usada para chegar à lua e funcionaria perfeitamente, infelizmente a tecnologia desapareceu e não podemos mais voltar à lua, mas você poderá usar o LIVENCRYPT em qualquer dispositivo, por mais antigo que seja. Mesmo que você tenha o modelo e os valores das sequências, você poderia criptografar e descriptografar manualmente.
    
        # O LIVENCRYPT pode ser usado para enviar fotos, vídeos e áudio criptografados?
        Obviamente, não agora, mas talvez no futuro.
    
        # Não há anúncios nem o aplicativo é pago. Qual é o truque?
        Fomos levados a acreditar que, se algo não tem valor e pode ser possuído por qualquer um, não tem valor para nós mesmos. No entanto, usamos plataformas "gratuitas" e no sistema não há nada gratuito, pois cada um de nós é um produto para eles e o algoritmo coleta todas as nossas ações para depois nos vender nossos interesses ou qualquer coisa que tenhamos comentado por meio de publicidade. Se você quer criar um bem para a Humanidade, não há maior alegria do que TODO SER HUMANO utilizá-lo sem impedimentos. Portanto, ficarei grato àqueles que compartilharem o aplicativo, usarem e àqueles que quiserem expressar sua gratidão com doações, compartilho as seguintes carteiras: 
        ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
        Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
        # Por que a licença GPLv3?
        Pela transparência, demonstrando que não há portas traseiras nem nada suspeito e para que qualquer um possa contribuir para melhorar o LIVENCRYPT.
    
        # Onde posso ver o código original?
        Você encontrará o código LIVENCRYPT 1.1 em: github.com/Synergia86 e gitee.com/Synergia_0ef4
    
        # Gostaria de relatar erros e sugerir ideias?
        Você pode não ter a menor ideia de programação, mas se quiser colaborar, acesse a comunidade no discord.gg/sDRawvyXhy para compartilhar os erros e ideias que tiver em mente.
    
        # Qualquer programador de verdade vai rir do código.
        Eu não ficaria surpreso, e alguns até arrancariam os cabelos depois de analisar todo o código. Eu o criei usando chatgpt e claude.ai, tenho que dizer que não foi nada fácil, muita calma e perseverança diante de milhares de tentativas e erros. Eu me formei em informática, mas não na área de programação, perdoem-me por não respeitar a estrutura. O mais importante é que FUNCIONA.
    
        # Não tenho nada a esconder, sou um bom escravo obediente às autoridades.
        Um dia você agradecerá à HUMANIDADE que decidiu dar o passo para fazer desta realidade uma melhor para o benefício comum de todos. Você pode seguir seu caminho como um NPC ou deixar sua marca, e sabe o melhor? Ambos os caminhos são igualmente válidos!
    
        # O sistema vai me investigar se eu usar o aplicativo.
        O sistema tem um registro detalhado de cada SER HUMANO desde o nascimento, e se não fizermos nada, acabaremos pagando por respirar.
    
        # Gênios que contribuíram para o bem da Humanidade acabaram tendo acidentes fatais. Você tem medo de que algo possa acontecer com você?
        Se eu tivesse medo, o LIVENCRYPT não teria visto a luz do dia. Estamos aqui para deixar nossa marca, e se eu tiver que partir, voltarei em outra vida para continuar incomodando. Quanto mais eles querem que tenhamos medo, mais devemos rir do show que eles criam. Infundir medo e acreditar nisso também nos mata! Riam e aproveitem o caminho!
        """,
                "Deutsch": """
        # Wofür ist LIVENCRYPT?
        LIVENCRYPT dient dazu, 100% private Gespräche zu führen. Jetzt bist du die erste Sicherheitsebene, indem du eine Verschlüsselung des Inhalts erstellst, und nur der Empfänger wird die Frequenz kennen, um den Inhalt zu entschlüsseln.
    
        # Gibt es kein Handbuch zur Nutzung von LIVENCRYPT?
        Text verschlüsseln: Unverschlüsselter Text wird verschlüsselt.
        Text entschlüsseln: Verschlüsselter Text wird entschlüsselt.
        Im Wert: nur Zahlen von 0 bis 1000.
        Wähle die Vorlage, die die hinzugefügten Zeichen im Text enthält, und klicke auf Ausführen, um das Ergebnis anzuzeigen.
        Passwort: In dieser Version, wenn du eines der folgenden Sonderzeichen im Text hinzufügst: ¢|@#~½¶←↓→ˀ|¢ª─¬, wird beim Ausführen nach einem Passwort gefragt, und du musst das Sonderzeichen aus dem Text und die folgenden 7 Zeichen (Leerzeichen zählen ebenfalls als Zeichen) hinzufügen. Beispiel: hallo~1234567890 wird nach dem Passwort fragen = ~1234567 und nach der Validierung wird der Text verschlüsselt. Um den verschlüsselten Text zu entschlüsseln, musst du dich an das Passwort erinnern. In diesem Fall musst du ~1234567 eingeben, um die Entschlüsselung auszuführen.
        Vorlagen verwalten: Vorlagen erstellen, beim Auswählen einer Sprache werden die Zeichen angezeigt, um sie einzeln hinzuzufügen oder die Schaltfläche "Alle hinzufügen" zu verwenden. In Zahlen/Zeichen findest du die Zahlen und Zeichen der Sprachen. Als Sonderzeichen gibt es das Leerzeichen "␣", das in der Verschlüsselung ausgeführt wird. Wenn es nicht hinzugefügt wird und du das Leerzeichen verwendest, werden Leerzeichen in der Verschlüsselung gelassen.
        Größe auswählen: Bezieht sich auf die Zeilen und Spalten, die die Vorlage haben wird. Du kannst die Standardwerte verwenden oder die gewünschten Werte hinzufügen, aber um die Vorlage speichern zu können, musst du den Zeichen-Zähler auf Null setzen.
        Zufälligkeit: Verschiebt die hinzugefügten Zeichen zufällig.
        Löschen: Entfernt alle hinzugefügten Zeichen.
        Letztes Zeichen löschen.
        Vorlage speichern: Gebe den Namen der Vorlage an und speichere.
        Zum Bearbeiten werden nur die erstellten Vorlagen angezeigt. Du kannst nur die Vorlagen löschen, die du erstellt hast. Die Standardvorlagen kannst du im Quellcode einsehen.
        Auf der Hauptseite gibt es ein Symbol in der oberen rechten Ecke, um auf die Einstellungen zuzugreifen. Du kannst die Sprache ändern, die Schriftgröße zwischen einem Wert von 8 und 24 ändern. Häufig gestellte Fragen, Tipps, Credits und Lizenz.

        # Um eine Datei zu verschlüsseln oder zu entschlüsseln. Wählen Sie die auszuführende Funktion, laden Sie die Datei hoch, geben Sie die Werte ein, führen Sie den Vorgang so oft wie nötig aus (es wird empfohlen, mindestens 2 Verschlüsselungen durchzuführen), und speichern Sie die Datei. Im Verschlüsselungsmodus werden die Dateien im hexadezimalen .txt-Format gespeichert, im Entschlüsselungsmodus wird nach der Dateierweiterung gefragt, und im nächsten Fenster wird sie im Binärformat gespeichert.
    
        # Ist es kompliziert, eine neue Vorlage mit jemandem zu teilen und die Position aller Zeichen abzugleichen?
        Nein, du musst nur die Größe (Zeilen/Spalten) angeben und alle Zeichen durch ein Komma getrennt teilen und die Vorlage speichern. Mit einer Verschlüsselungssequenz unter Verwendung der Standardvorlagen kannst du die Zeichen der neuen Vorlage einfügen und die neue verschlüsselte Vorlage senden.
    
        # Ich kann die Person nicht treffen, um die Platzierung der Zeichen in der erstellten Vorlage anzugeben. Was kann ich tun?
        Wenn ihr euch nicht persönlich treffen könnt, müsst ihr eine Möglichkeit finden, die Wertesequenz so auszutauschen, dass, wenn der Algorithmus eure Gespräche überprüft, er nicht erkennt, dass ihr Werte teilt, und wenn er es erkennt, verwendet ihr nicht dasselbe Medium, sondern verschiedene, mit Anweisungen, die nur ihr beide versteht und die Werte verändern, aber der Algorithmus kann nicht interpretieren, dass es sich um Werte handelt. Zusätzlich zu den Standardvorlagen, sobald ihr die Sequenz habt, könnt ihr neue Vorlagen erstellen und Details in den verschlüsselten Nachrichten angeben.
    
        # Würdest du weitere Änderungen vornehmen?
        Ja, ich habe darüber nachgedacht, eine Kontrolle über die Passwortwerte hinzuzufügen und die Zeichen, die als Passwort zugewiesen werden können, hinzuzufügen/zu bearbeiten. Kopiere und füge ein Sonderzeichen in den Text ein, wenn du das Passwort in deiner Verschlüsselung aktivieren möchtest, auch wenn deine Sprache das Zeichen nicht bereitstellt.
    
        # Wird es in weiteren Sprachen übersetzt?
        Ja, ich werde weiterhin daran arbeiten, es für alle zugänglich zu machen. Trete dem discord.gg/sDRawvyXhy bei und fordere deine Sprache an. Um ehrlich zu sein, LIVENCRYPT muss nicht in deiner Sprache sein, es ist sehr intuitiv, sogar beim Erstellen einer neuen Vorlage kannst du neue Zeichen hinzufügen, die in den aufgelisteten Sprachen nicht vorhanden sind.
    
        # Werden neue Möglichkeiten zum Teilen der Verschlüsselung geschaffen?
        Ja, ich habe vor, Interaktionen in von KI erstellten virtuellen Szenarien mit der Möglichkeit von Sprachgesprächen über web3 und P2P-Verbindungen zu schaffen. Die Szenarien wären einzigartig und würden nach der Sitzung gelöscht.
    
        # Was sind die Anforderungen für die Anwendung?
        Es kann ohne Internetzugang verwendet werden und könnte die Technologie verwenden, die zum Mond führte und perfekt funktioniert, leider ist die Technologie verschwunden und wir können nicht mehr zum Mond zurückkehren, aber du kannst LIVENCRYPT auf jedem Gerät verwenden, egal wie alt es ist. Sogar wenn du die Vorlage und die Wertesequenzen hast, könntest du es manuell verschlüsseln und entschlüsseln.
    
        # Kann LIVENCRYPT zum Senden verschlüsselter Fotos, Videos und Audiodaten verwendet werden?
        Natürlich jetzt nicht, aber vielleicht eines Tages ja.
    
        # Es gibt keine Werbung und die Anwendung ist nicht kostenpflichtig. Wo ist der Haken?
        Uns wurde beigebracht zu glauben, dass, wenn etwas keinen Wert hat und von jedem besessen werden kann, es für uns selbst keinen Wert hat. Wir nutzen jedoch "kostenlose" Plattformen und im System gibt es nichts Kostenloses, denn jeder von uns ist ein Produkt für sie, und der Algorithmus sammelt all unsere Aktionen, um uns später unsere Interessen oder alles, was wir kommentiert haben, durch Werbung zu verkaufen. Wenn du ein Wohl für die Menschheit schaffen möchtest, gibt es keine größere Freude, als dass JEDER MENSCH es ohne Hindernisse nutzt. Daher werde ich dankbar sein für diejenigen, die die Anwendung teilen, nutzen und für diejenigen, die ihre Dankbarkeit mit Spenden zeigen möchten, teile ich die folgenden Wallets:
        ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
        Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
        # Warum die GPLv3-Lizenz?
        Aus Transparenzgründen, um zu zeigen, dass es keine Hintertüren oder verdächtige Elemente gibt, und damit jeder einen Beitrag zur Verbesserung von LIVENCRYPT leisten kann.
    
        # Wo kann man den Originalcode einsehen?
        Den LIVENCRYPT 1.1-Code findest du unter: github.com/Synergia86 und gitee.com/Synergia_0ef4
    
        # Ich möchte Fehler melden und Ideen vorschlagen?
        Du musst keine Ahnung von Programmierung haben, aber wenn du mitmachen möchtest, tritt der discord.gg/sDRawvyXhy-Community bei, um die Fehler und Ideen zu teilen, die du im Kopf hast.
    
        # Jeder echte Programmierer wird über den Code lachen.
        Ich wäre nicht überrascht, und einige werden sich sogar die Haare raufen, nachdem sie den gesamten Code analysiert haben. Ich habe ihn mit chatgpt und claude.ai erstellt, ich muss sagen, es war überhaupt nicht einfach, viel Geduld und Beharrlichkeit bei Tausenden von Versuchen und Fehlern. Ich habe Informatik studiert, aber nicht im Bereich Programmierung, entschuldigt bitte, dass ich die Struktur nicht respektiert habe. Das Wichtigste ist, dass es FUNKTIONIERT.
    
        # Ich habe nichts zu verbergen, ich bin ein guter Sklave, der den Behörden gehorcht.
        Eines Tages wirst du der MENSCHHEIT danken, die den Schritt gewagt hat, diese Realität zum Wohle aller zu verbessern. Du kannst deinen Weg als NPC gehen oder deinen Fußabdruck hinterlassen, und weißt du, was das Beste ist? Beide Wege sind gleichermaßen gültig!
    
        # Das System wird mich untersuchen, wenn ich die Anwendung nutze.
        Das System hat ein detailliertes Register jedes MENSCHEN seit seiner Geburt, und wenn wir nichts tun, werden wir am Ende dafür bezahlen, dass wir atmen.
    
        # Genies, die zum Wohl der Menschheit beigetragen haben, hatten tödliche Unfälle. Hast du Angst, dass dir etwas passieren könnte?
        Wenn ich Angst hätte, hätte LIVENCRYPT nie das Licht der Welt erblickt. Wir sind hier, um unseren Fußabdruck zu hinterlassen, und wenn ich gehen muss, werde ich in einem anderen Leben zurückkehren, um weiterhin zu nerven. Je mehr sie wollen, dass wir Angst haben, desto mehr müssen wir über die Show lachen, die sie erschaffen. Angst zu verbreiten und daran zu glauben, tötet uns auch! Lacht und genießt den Weg!
        """,
                "日本語": """
        # LIVENCRYPTは何のためにありますか？
        LIVENCRYPTは、100%プライベートな会話を維持するためのものです。今、あなたは最初のセキュリティレベルとなり、コンテンツを暗号化して作成し、受信者だけがコンテンツを解読するための周波数を知ることができます。
    
        # LIVENCRYPTを使用するためのマニュアルはありませんか？
        テキストを暗号化：暗号化されていないテキストが暗号化されます。
        テキストを復号化：暗号化されたテキストが復号化されます。
        値では：0から1000までの数字のみ。
        追加された文字を含むテンプレートを選択し、実行をクリックして結果を表示します。
        パスワード：このバージョンでは、次の特殊文字のいずれかをテキストに追加すると： ¢|@#~½¶←↓→ˀ|¢ª─¬、実行時にパスワードの挿入を求められ、テキストの特殊文字と次の7文字（スペースも文字としてカウントされます）を追加する必要があります。例：こんにちは~一二三四五六七八九零 はパスワードの挿入を求められ = ~一二三四五六七 が検証されると、テキストが暗号化されます。暗号化されたテキストを復号化するには、パスワードを覚えている必要があります。この場合、復号化を実行するには ~一二三四五六七 を入力する必要があります。
        テンプレートを管理：テンプレートを作成し、言語を選択すると、文字を個別に追加するか、「すべて追加」ボタンを使用して追加する文字が表示されます。数字/記号には、言語の数字と記号が含まれています。特殊文字として「␣」スペースがあり、暗号化時に実行されます。追加しない場合、スペースを使用すると、暗号化にスペースが残ります。
        サイズを選択：テンプレートの行と列を指します。デフォルト値を使用することも、希望する値を追加することもできますが、テンプレートを保存するには、文字カウンターをゼロにする必要があります。
        ランダム化：追加された文字をランダムに移動します。
        クリア：追加されたすべての文字を削除します。
        最後の文字を削除。
        テンプレートを保存：テンプレートの名前を指定して保存します。
        編集するには、作成されたテンプレートのみが表示されます。作成したテンプレートのみを削除できます。デフォルトのテンプレートはソースコードを見て確認できます。
        メインページの右上隅に設定にアクセスするためのアイコンがあります。言語を変更し、フォントサイズを8から24の間で変更できます。よくある質問、ヒント、クレジット、ライセンス。

        # ファイルを暗号化または復号化するには、実行する機能を選択し、ファイルをアップロードして、値を入力し、必要な回数だけ実行します（最低でも2回の暗号化を推奨）。暗号化モードでは、ファイルは16進数の .txt 形式で保存され、復号化モードでは、ファイルの拡張子を要求され、次のウィンドウでバイナリ形式で保存されます。
    
        # 新しいテンプレートを他の人と共有し、すべての文字の位置を合わせるのは難しいですか？
        いいえ、サイズ（行/列）を指定し、すべての文字をカンマで区切って共有し、テンプレートを保存するだけです。デフォルトのテンプレートを使用して暗号化シーケンスを持っていれば、新しいテンプレートの文字を貼り付けて、新しい暗号化テンプレートを送信できます。
    
        # テンプレートの作成時に文字の配置を教えるために人と会うことができません。どうすればいいですか？
        直接会えない場合は、アルゴリズムが会話を検査しているときに値を共有していることが分からないように、値のシーケンスを交換する方法を工夫する必要があります。また、同じメディアを使用せず、異なるメディアを使用して、あなた方だけが理解できる指示で値を変更し、アルゴリズムがそれが値に関連していると解釈できないようにします。さらに、デフォルトのテンプレートを使用し、一度シーケンスが完了したら、新しいテンプレートを作成して暗号化メッセージで詳細を提供できます。
    
        # 追加の変更を加えますか？
        はい、パスワード値の制御を追加し、パスワードとして割り当てられる文字を追加/編集できるようにすることを考えています。言語に特殊文字がない場合でも、パスワードを暗号化に有効にしたい場合は、特殊文字をテキストにコピーして貼り付けます。
    
        # さらに多くの言語に翻訳されますか？
        はい、すべての人がアクセスできるようにし続けます。discord.gg/sDRawvyXhy にアクセスして自分の言語をリクエストしてください。正直なところ、LIVENCRYPTがあなたの言語である必要はありません。それは非常に直感的で、新しいテンプレートを作成する際に、リストされていない言語の新しい文字を追加することもできます。
    
        # 暗号化を共有する新しい方法は作成されますか？
        はい、私はAIが作成した仮想シナリオでの対話を考えています。web3とP2P接続を使用して音声会話のオプションもあります。シナリオはユニークで、セッション終了後に削除されます。
    
        # アプリケーションの要件は何ですか？
        インターネットに接続せずに使用でき、月に行くために使用された技術を使用して完全に動作しますが、残念ながらその技術は失われており、もはや月に戻ることはできませんが、非常に古いデバイスでもLIVENCRYPTを使用できます。テンプレートとシーケンスの値を持っていれば、手動で暗号化して復号化することもできます。
    
        # LIVENCRYPT を使用して、暗号化された写真、ビデオ、オーディオを送信できますか?
        現在はもちろんできませんが、将来的には可能です。
    
        # 広告もなく、アプリケーションは無料ですが、何か裏があるのですか？
        価値がないもの、誰でも持てるものは、自分自身には価値がないと信じるように教えられました。しかし、私たちは「無料」のプラットフォームを使用しており、システムには無料のものは何もありません。私たち一人一人が彼らにとっての商品であり、アルゴリズムは私たちのすべての行動を収集し、後で私たちの興味やコメントしたものを広告で売ろうとします。人類のために良いものを作りたいなら、すべての人が障害なく使用することに勝る喜びはありません。そのため、アプリケーションを共有し、使用し、感謝の気持ちを寄付で示してくれる人たちに感謝します。以下のウォレットを共有します：
        イーサリアム 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
        ソラナ FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        ビットコイン bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        モネロ 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
        # なぜGPLv3ライセンスなのですか？
        透明性のために、バックドアや疑わしいものがないことを示し、誰でもLIVENCRYPTの改善に貢献できるようにするためです。
    
        # オリジナルのコードはどこで見られますか？
        LIVENCRYPT 1.1コードは、github.com/Synergia86およびgitee.com/Synergia_0ef4で見つけることができます。
    
        # エラーを報告し、アイデアを提案したいですか？
        プログラミングの知識がなくても、参加したい場合は、discord.gg/sDRawvyXhy コミュニティに参加して、考えているエラーやアイデアを共有してください。
    
        # 本物のプログラマーはコードを見て笑うでしょう。
        それは驚くべきことではなく、一部の人はコードを分析した後、髪を引き抜くかもしれません。私はchatgptとclaude.aiを使用して作成しました。非常に多くの試行錯誤がありましたが、辛抱強く粘り強く取り組む必要がありました。私はコンピュータサイエンスを学びましたが、プログラミングの分野ではありません。構造を尊重しなかったことをお詫びします。最も重要なことは、それが動作することです。
    
        # 隠すものは何もなく、当局に従う良い奴隷です。
        ある日、人類のためにこの現実を改善するためのステップを踏み出したことに感謝するでしょう。NPCとしての道を進むか、自分の足跡を残すか、どちらも同じように有効です！
    
        # アプリケーションを使用するとシステムが私を調査します。
        システムは誕生以来、各人の詳細な記録を持っており、何もしなければ、最終的には呼吸するために支払うことになるでしょう。
    
        # 人類のために貢献した天才たちは致命的な事故に遭いました。あなたは何かが起こることを恐れていますか？
        恐れていたら、LIVENCRYPTは決して日の目を見なかったでしょう。私たちは自分の足跡を残すためにここにおり、去らなければならない場合は、別の人生で戻ってきて再び迷惑をかけます。彼らが私たちに恐怖を感じさせようとするほど、私たちは彼らが作り上げたショーを笑わなければなりません。恐怖を広め、それを信じることもまた私たちを殺します！笑って道を楽しみましょう！
        """,
                "Türkçe": """
        # LIVENCRYPT ne işe yarar?
        LIVENCRYPT, %100 özel konuşmalar yapmak için kullanılır. Artık içeriği şifreleyerek ilk güvenlik seviyesini sen oluşturuyorsun ve sadece alıcı, içeriği çözmek için gerekli frekansı bilecek.
    
        # LIVENCRYPT'i kullanmak için bir kılavuz yok mu?
        Metni şifrele: şifrelenmemiş metin şifrelenecektir.
        Metni çöz: şifreli metin çözülecektir.
        Değerde: sadece 0'dan 1000'e kadar sayılar.
        Metne eklenen karakterleri içeren şablonu seç ve sonucu göstermek için çalıştır.
        Şifre: Bu sürümde metne şu özel karakterlerden birini eklediğinde: ¢|@#~½¶←↓→ˀ|¢ª─¬ çalıştırdığında şifre eklemen istenecek ve metnin özel karakteri ve sonraki 7 karakteri eklemen gerekecek (boşluk da karakter olarak sayılır). Örnek: merhaba~1234567890 şifre eklemeni isteyecek = ~1234567 ve doğrulandığında metin şifrelenecektir. Şifreli metni çözme işlevini kullanırken şifreyi hatırlaman gerekecek, bu durumda çözme işlemini gerçekleştirmek için ~1234567 girmen gerekecek.
        Şablonları yönet: şablonlar oluştur, bir dil seçtiğinde karakterleri bireysel olarak eklemek veya tümünü ekle düğmesini kullanmak için gösterir. Sayılar/işaretler bölümünde dillerin sayı ve işaretleri bulunur. Özel karakter olarak boşluk "␣" şifrelemede çalıştırmak için vardır, eklemezsen ve boşluk kullanırsan şifrelemede boşluklar kalır.
        Boyutu seç: şablonun satır ve sütunlarını belirler. Varsayılan değerleri kullanabilir veya istediğin değerleri ekleyebilirsin, ancak şablonu kaydetmek için karakter sayacını sıfırda bırakman gerekecek.
        Karıştır: eklenen karakterleri rastgele taşır.
        Temizle: eklenen tüm karakterleri siler.
        Son karakteri sil.
        Şablonu kaydet: şablonun adını belirt ve kaydet.
        Düzenlemek için yalnızca oluşturulan şablonlar görüntülenecektir. Yalnızca oluşturduğun şablonları silebilirsin. Varsayılan şablonlar kaynak kodunu görerek görüntülenebilir.
        Ana sayfanın sağ üst köşesinde ayarlara erişmek için bir simge vardır. Dili değiştirir, yazı tipi boyutunu 8 ile 24 arasında değiştirir. Sıkça Sorulan Sorular, ipuçları, krediler ve lisans.

        # Bir dosyayı şifrelemek veya şifresini çözmek için. Yapılacak işlemi seçin, dosyayı yükleyin, değerleri girin, gerektiği kadar çalıştırın (en az 2 şifreleme yapılması tavsiye edilir) ve dosyayı kaydedin. Şifreleme modunda, dosyalar onaltılık .txt formatında kaydedilir, şifre çözme modunda ise sizden dosyanın sahip olması gereken uzantı istenecektir ve bir sonraki pencerede dosya ikili olarak kaydedilecektir.
    
        # Yeni bir şablonu başkasıyla paylaşmak ve tüm karakterlerin konumlarını eşleştirmek zor mu?
        Hayır, sadece boyutu (satır/sütun) belirtmen ve tüm karakterleri virgülle ayırıp paylaşman ve şablonu kaydetmen yeterli. Varsayılan şablonları kullanarak bir şifreleme dizisi oluşturursan, yeni şablon karakterlerini yapıştırabilir ve yeni şifreli şablonu gönderebilirsin.
    
        # Oluşturduğum şablondaki karakterlerin yerleşimini bildirmek için kişiyle buluşamıyorum, ne yapabilirim?
        Kişisel olarak buluşamazsanız, algoritmanın konuşmalarınızı gözden geçirirken değerleri paylaştığınızı fark etmemesi için değerlerin dizisini değiştirmenin bir yolunu bulmanız gerekecek. Algoritmanın bunu fark etmesi durumunda aynı medyayı kullanmak yerine farklı medyalar kullanarak sadece ikinizin anlayacağı talimatlarla değerleri değiştirin, algoritma bu değerlerin ilişkili olduğunu anlamayacaktır. Ayrıca, varsayılan şablonları kullanarak, diziyi oluşturduktan sonra, şifreli mesajlarda ayrıntılar sağlayarak yeni şablonlar oluşturabilirsiniz.
    
        # Daha fazla değişiklik yapar mısın?
        Evet, şifre değerleri üzerinde kontrol eklemeyi ve şifre olarak atanabilecek karakterleri ekleyip düzenlemeyi düşünüyorum. Diliniz özel karakter içermese bile, şifrenizi etkinleştirmek için özel karakteri metne kopyalayıp yapıştırabilirsiniz.
    
        # Daha fazla dile çevrilecek mi?
        Evet, herkesin erişebilmesi için çalışmaya devam edeceğim. discord.gg/sDRawvyXhy 'a erişip kendi dilinizi talep edebilirsiniz. Dürüst olmak gerekirse, LIVENCRYPT'in dilinizde olması gerekmez, çok sezgiseldir ve listedeki dillerde olmayan yeni karakterleri eklemenize olanak tanır.
    
        # Şifreleme paylaşmanın yeni yolları oluşturulacak mı?
        Evet, AI tarafından oluşturulan sanal senaryolarda etkileşimi düşünüyorum. Web3 ve P2P bağlantılarını kullanarak sesli sohbet seçeneği de olacak. Senaryolar benzersiz olacak ve oturum sonunda silinecek.
    
        # Uygulamanın gereksinimleri nelerdir?
        İnternete erişmeden kullanılabilir ve aya gitmek için kullanılan teknolojiyle tamamen çalışabilir, ancak ne yazık ki bu teknoloji kayboldu ve artık aya geri dönemiyoruz, ancak çok eski cihazlarda bile LIVENCRYPT kullanabilirsiniz. Şablonlar ve dizilerin değerleri varsa, manuel olarak şifreleyip çözebilirsiniz.
    
        # LIVENCRYPT şifrelenmiş fotoğraf, video ve ses göndermek için kullanılabilir mi?
        Şu anda değil, ama belki yarın olabilir.
    
        # Uygulama reklam içermiyor ve ücretsiz, hile nedir?
        Bize bir şeyin değeri yoksa ve herkes sahip olabiliyorsa, kendimiz için değersiz olduğuna inanmamız öğretildi. Ancak "ücretsiz" platformları kullanıyoruz ve sistemde hiçbir şey ücretsiz değil, çünkü her birimiz onlar için bir ürünüz ve algoritma tüm eylemlerimizi toplayarak sonrasında ilgilerimizi veya yorumladığımız herhangi bir şeyi reklamlarda satmaya çalışıyor. İnsanlık için iyi bir şey yaratmak istiyorsanız, herkesin herhangi bir engel olmadan kullanması kadar büyük bir sevinç yoktur. Bu nedenle, uygulamayı paylaşan, kullanan ve bağışlarla minnettarlıklarını gösterenlere minnettarım. Aşağıdaki cüzdanları paylaşıyorum: 
        ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
        Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
        # Neden GPLv3 lisansı?
        Şeffaflık için, arka kapı veya şüpheli bir şey olmadığını göstermek ve herkesin LIVENCRYPT'i geliştirmeye katkıda bulunabilmesi için.
    
        # Orijinal kodu nerede görebilirim?
        LIVENCRYPT 1.1 kodunu github.com/Synergia86 ve gitee.com/Synergia_0ef4 adreslerinde bulabilirsiniz.
    
        # Hataları bildirmek ve fikirler önermek ister misiniz?
        Programlama hakkında hiçbir bilginiz olmasa bile katılmak istiyorsanız, hatalarınızı ve fikirlerinizi paylaşmak için discord.gg/sDRawvyXhy topluluğuna katılabilirsiniz.
    
        # Gerçek bir programcı kodu görünce gülecek.
        Bu hiç şaşırtıcı değil ve bazıları kodu analiz ettikten sonra saçlarını yolacaklar. Bunu chatgpt ve claude.ai kullanarak yarattım. Çok sayıda deneme ve hata vardı, ancak sabır ve azimle çalışmak gerekiyordu. Bilgisayar bilimi okudum ama programlama dalında değil. Yapıyı ihmal ettiğim için özür dilerim. En önemli şey, ÇALIŞIYOR olmasıdır.
    
        # Gizleyecek bir şeyim yok, otoritelerin söylediği şeylere uyan iyi bir köleyim.
        Bir gün insanlık için bu gerçeği iyileştirmek için adım atan insanlara minnettar olacaksınız. Bir NPC olarak kendi yolunuzu izleyebilirsiniz veya kendi izinizi bırakabilirsiniz ve en iyisi nedir biliyor musunuz? Her iki yol da eşit derecede geçerlidir!
    
        # Uygulamayı kullanırsam sistem beni araştıracak.
        Sistem doğumdan itibaren her insanın ayrıntılı kayıtlarını tutar ve bir şey yapmazsak, sonunda nefes almak için ödeme yapmamız gerekecek.
    
        # İnsanlık için katkıda bulunan dâhiler ölümcül kazalar geçirdiler, başıma bir şey gelmesinden korkuyor musun?
        Korksaydım, LIVENCRYPT asla gün ışığını göremezdi. Buradayız izimizi bırakmak için ve eğer gitmem gerekirse, başka bir hayatta geri döner ve tekrar rahatsız ederim. Korkmamızı istedikleri kadar, onların yarattığı gösteriye gülmemiz gerekir. Korkuyu yaymak ve buna inanmak da bizi öldürür! Gülün ve yolun tadını çıkarın!
        """,
                "한국어": """
        # LIVENCRYPT는 무엇에 사용됩니까?
        LIVENCRYPT는 100% 개인 대화를 유지하는 데 사용됩니다. 이제 당신은 내용을 암호화하여 첫 번째 보안 수준을 만들고, 오직 수신자만이 내용을 복호화하는 주파수를 알게 됩니다.
    
        # LIVENCRYPT를 사용하는 매뉴얼이 없습니까?
        텍스트 암호화: 암호화되지 않은 텍스트가 암호화됩니다.
        텍스트 복호화: 암호화된 텍스트가 복호화됩니다.
        값: 0에서 1000 사이의 숫자만.
        텍스트에 추가된 문자를 포함하는 템플릿을 선택하고 실행하여 결과를 보여줍니다.
        비밀번호: 이 버전에서는 텍스트에 다음 특수 문자 중 하나를 추가하면: ¢|@#~½¶←↓→ˀ|¢ª─¬ 실행 시 비밀번호를 입력하라는 메시지가 표시되며, 텍스트의 특수 문자와 다음 7개의 문자를 추가해야 합니다 (공백도 문자로 간주됩니다). 예: 안녕하세요~하나둘셋넷다섯여섯일곱여덟아홉제로비밀번호 입력 요청 = ~하나둘셋넷다섯여섯일곱 확인되면 텍스트가 암호화됩니다. 암호화된 텍스트를 복호화 기능을 사용할 때 비밀번호를 기억해야 하며, 이 경우 복호화를 실행하려면 ~하나둘셋넷다섯여섯일곱 입력해야 합니다.
        템플릿 관리: 템플릿 생성, 언어를 선택하면 문자를 개별적으로 추가하거나 모두 추가 버튼을 사용할 수 있습니다. 숫자/기호에서 각 언어의 숫자와 기호를 찾을 수 있습니다. 특수 문자로 공백 "␣"이 있으며, 암호화에 포함되지 않으면 암호화 시 공백이 남습니다.
        크기 선택: 템플릿의 행과 열을 설정합니다. 기본값을 사용하거나 원하는 값을 추가할 수 있지만, 템플릿을 저장하려면 문자를 0으로 남겨야 합니다.
        무작위화: 추가된 문자를 무작위로 이동합니다.
        지우기: 추가된 모든 문자를 제거합니다.
        마지막 문자 삭제.
        템플릿 저장: 템플릿 이름을 지정하고 저장합니다.
        편집하려면 생성된 템플릿만 표시됩니다. 생성한 템플릿만 삭제할 수 있습니다. 기본 템플릿은 소스 코드를 확인하여 볼 수 있습니다.
        메인 화면 오른쪽 상단에 설정에 접근할 수 있는 아이콘이 있습니다. 언어를 변경하고, 글꼴 크기를 8에서 24까지 변경합니다. 자주 묻는 질문, 팁, 크레딧 및 라이선스를 포함합니다.

        # 파일을 암호화하거나 복호화하려면 수행할 기능을 선택하고 파일을 업로드한 후 값을 입력하고 필요한 만큼 실행합니다(최소 2회 암호화 권장). 암호화 모드에서는 파일이 16진수 .txt 형식으로 저장되며, 복호화 모드에서는 파일의 확장자를 묻고 다음 창에서 바이너리로 저장됩니다.
    
        # 새로운 템플릿을 다른 사람과 공유하고 모든 문자의 위치를 일치시키는 것이 어렵습니까?
        아니요, 크기(행/열)를 알려주고 모든 문자를 쉼표로 구분하여 공유하고 템플릿을 저장하면 됩니다. 기본 템플릿을 사용하여 암호화 시퀀스를 만들면 새 템플릿의 문자를 붙여넣고 새 암호화된 템플릿을 보낼 수 있습니다.
    
        # 내가 만든 템플릿의 문자의 위치를 알려주기 위해 상대와 만날 수 없으면 어떻게 해야 합니까?
        직접 만날 수 없다면, 알고리즘이 대화를 검토할 때 값을 공유하는 것을 눈치채지 않도록 값의 시퀀스를 변경하는 방법을 찾아야 합니다. 알고리즘이 이를 눈치챈다면 동일한 매체를 사용하지 말고, 둘만 이해할 수 있는 지침을 사용하여 서로 다른 매체를 사용하여 값을 변경하십시오. 또한 기본 템플릿을 사용하여 시퀀스를 만든 후, 암호화된 메시지에서 세부 사항을 제공하여 새 템플릿을 만들 수 있습니다.
    
        # 더 많은 변경 사항을 추가하시겠습니까?
        예, 비밀번호 값에 대한 제어를 추가하고 비밀번호로 지정할 수 있는 문자를 추가/편집하는 기능을 추가할 생각입니다. 언어에 특수 문자가 없더라도 텍스트에 특수 문자를 복사하여 붙여넣어 암호화를 활성화할 수 있습니다.
    
        # 더 많은 언어로 번역될 예정입니까?
        예, 모두가 접근할 수 있도록 계속 작업할 것입니다. 디스코드에 접속하여 원하는 언어를 요청하십시오. 솔직히 말해서, LIVENCRYPT가 당신의 언어로 제공될 필요는 없습니다. 매우 직관적이며, 새로운 템플릿을 만들 때 나열된 언어에 없는 새 문자를 추가할 수 있습니다.
    
        # 암호화 공유의 새로운 방법이 만들어질 것입니까?
        예, AI가 생성한 가상 시나리오에서 상호작용을 생각하고 있습니다. Web3 및 P2P 연결을 사용하여 음성 대화 옵션도 있을 것입니다. 시나리오는 고유하며 세션이 끝나면 삭제됩니다.
    
        # 애플리케이션의 요구 사항은 무엇입니까?
        인터넷에 접근하지 않고 사용할 수 있으며, 달에 가기 위해 사용된 기술로 완벽하게 작동할 것입니다. 하지만 불행히도 그 기술은 사라졌고 더 이상 달에 갈 수 없지만, 매우 오래된 장치에서도 LIVENCRYPT를 사용할 수 있습니다. 템플릿과 시퀀스 값을 가지고 있다면 수동으로 암호화하고 복호화할 수 있습니다.
    
        # LIVENCRYPT를 사용하여 암호화된 사진, 비디오, 오디오를 보낼 수 있나요?
        현재는 아니지만, 언젠가 가능할 것입니다.
    
        # 애플리케이션이 광고도 없고 무료라면 속임수가 무엇입니까?
        우리는 가치가 없거나 누구나 가질 수 있는 것이 우리 자신에게는 가치가 없다고 믿도록 만들어졌습니다. 그러나 "무료" 플랫폼을 사용하고 있으며, 시스템에서는 아무것도 무료가 아닙니다. 왜냐하면 우리 각자는 그들에게 하나의 제품이기 때문이며, 알고리즘은 모든 행동을 수집하여 이후에 우리의 관심사나 우리가 언급한 어떤 것을 광고로 판매하려고 하기 때문입니다. 인류를 위한 좋은 것을 만들고 싶다면, 모든 사람이 아무런 제약 없이 사용하는 것만큼 큰 기쁨은 없습니다. 따라서 애플리케이션을 공유하고 사용하고, 감사의 마음을 기부로 보여주는 사람들에게 감사드립니다. 다음 지갑을 공유합니다 
        이더리움 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71 
        솔라나 FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
        비트코인 bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
        모네로 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
        # 왜 GPLv3 라이선스입니까?
        투명성을 위해, 백도어나 의심스러운 것이 없음을 보여주고, 누구나 LIVENCRYPT를 개선하는 데 기여할 수 있도록 하기 위해서입니다.
    
        # 원본 코드를 어디서 볼 수 있습니까?
        LIVENCRYPT 1.1 코드는 github.com/Synergia86 및 gitee.com/Synergia_0ef4에서 찾을 수 있습니다.
    
        # 버그를 보고하고 아이디어를 제안하고 싶습니까?
        프로그래밍에 대한 지식이 전혀 없어도 참여하고 싶다면, 디스코드 커뮤니티에 접속하여 버그와 아이디어를 공유할 수 있습니다.
    
        # 진정한 프로그래머는 코드를 보고 웃을 것입니다.
        전혀 놀랍지 않으며, 일부는 코드를 분석한 후 자신의 머리카락을 뽑을 것입니다. 이것을 chatgpt와 claude.ai를 사용하여 만들었습니다. 수많은 시도와 오류가 있었지만, 침착함과 인내심을 가지고 작업해야 했습니다. 컴퓨터 과학을 전공했지만, 프로그래머는 아닙니다. 구조를 무시한 것에 대해 사과드립니다. 가장 중요한 것은, 작동한다는 것입니다.
    
        # 숨길 것이 없습니다. 당국이 말하는 것을 따르는 좋은 노예입니다.
        언젠가 이 현실을 더 나은 것으로 만들기 위해 한 걸음 나아간 인류에게 감사할 것입니다. NPC로서 자신의 길을 갈 수도 있고, 자신의 흔적을 남길 수도 있습니다. 가장 좋은 점은 무엇일까요? 두 가지 길 모두 똑같이 유효합니다!
    
        # 애플리케이션을 사용하면 시스템이 나를 조사할 것입니다.
        시스템은 태어날 때부터 모든 인간의 세부 기록을 가지고 있으며, 아무것도 하지 않으면 결국 숨쉬는 것에 대해 비용을 지불해야 할 것입니다.
    
        # 인류를 위해 기여한 천재들은 치명적인 사고를 당했는데, 무언가가 일어날까 두렵습니까?
        두려웠다면, LIVENCRYPT는 결코 빛을 보지 못했을 것입니다. 우리는 여기서 우리의 흔적을 남기기 위해 있으며, 떠나야 한다면 다음 생에서 다시 돌아와 성가시게 할 것입니다. 두려워할수록 그들이 만든 쇼에 웃어야 합니다. 두려움을 퍼뜨리고 믿는 것도 우리를 죽입니다! 웃고 여정을 즐기세요!
        """,
            }
    def definir_consejos_texto(self):
        self.consejos_texto = {
                "Español": """
    1. Usa la aplicación en un dispositivo sin conexión a Internet como Raspberry Pi, Orange Pi Plus,... 
    2. Realiza un descifrado con contraseña en el que caso que lo tenga para comprobar que el cifrado se realizó correctamente.
    3. Crea tus propias plantillas, añade el espacio representando como "␣" para que todo el contenido quede cifrado y pega nuevos caracteres que no estén en la lista de idiomas para añadir nuevos caracteres.
    4. Crea cifrados múltiples con contraseña y diferentes plantillas dando saltos entre idiomas. 
    5. Consensuar en persona el primer cifrado para volverlo más complejo dando instrucciones en el mensaje cifrado.
    6. Crear decenas y cientos de mensajes cifrados falsos corriendo por Internet.
    7. No guardes la secuencia de valores en ningún dispositivo con Internet, de hacerlo no pongas el real, pon un valor al que tengas que sumar tu día y mes de cumpleaños o algo del estilo que te sea fácil recordar.
    8. No uses copiar y pegar texto original en un dispositivo que se conecta a Internet ya que se queda almacenado en la memoria RAM. Solamente usar el copiar y pegar cuando el texto esté cifrado.
                """,
                "English": """
    1. Use the application on an offline device like Raspberry Pi, Orange Pi Plus,...
    2. Perform a password decryption to verify that the encryption was done correctly.
    3. Create your own templates, add the space represented as "␣" so that all content is encrypted, and paste new characters that are not in the language list to add new characters.
    4. Create multiple encryptions with passwords and different templates, jumping between languages.
    5. Agree in person on the first encryption to make it more complex by giving instructions in the encrypted message.
    6. Create dozens and hundreds of fake encrypted messages running on the Internet.
    7. Don't save the sequence of values on any device with Internet access. If you do, don't put the real one, put a value to which you have to add your birthday and month or something similar that is easy for you to remember.
    8. Do not copy and paste original text on a device that connects to the Internet as it gets stored in the RAM. Only use copy and paste when the text is encrypted.
                """,
                "中文": """
    一。在离线设备上使用应用程序，例如 Raspberry Pi、Orange Pi Plus 等...
    二。如果有密码，请进行密码解密以验证加密是否正确完成。
    三。创建您自己的模板，添加空格表示为"␣"以确保所有内容都被加密，并粘贴不在语言列表中的新字符以添加新字符。
    四. 四.使用密码和不同的模板创建多重加密，在语言之间跳转。
    五。亲自商定第一次加密，通过在加密消息中给出指令使其更复杂。
    六。在互联网上创建数十个甚至上百个虚假的加密消息。
    七。不要将值序列保存在任何连接互联网的设备上，如果这样做，不要使用真实值，而是使用一个你需要加上生日的月份和日期或类似容易记住的东西的值。
    八。不要在连接互联网的设备上复制和粘贴原始文本，因为它会存储在 RAM 中。只有在文本加密时才使用复制和粘贴
                """,
                "हिन्दी": """
    एक। Raspberry Pi, Orange Pi Plus जैसे ऑफ़लाइन डिवाइस पर ऐप्लिकेशन का उपयोग करें,...
    दो। यदि पासवर्ड है तो एन्क्रिप्शन की सही तरह से जांच करने के लिए पासवर्ड के साथ डिक्रिप्शन करें।
    तीन। अपने खुद के टेम्प्लेट बनाएं, स्पेस को "␣" के रूप में दर्शाएं ताकि सारी सामग्री एन्क्रिप्ट हो जाए और नए अक्षर जोड़ने के लिए भाषाओं की सूची में न होने वाले नए अक्षरों को पेस्ट करें।
    चार। पासवर्ड और विभिन्न टेम्प्लेट्स के साथ मल्टीपल एन्क्रिप्शन बनाएं, भाषाओं के बीच छलांग लगाते हुए।
    पाँच। पहले एन्क्रिप्शन को व्यक्तिगत रूप से सहमत करें ताकि एन्क्रिप्टेड संदेश में निर्देश देकर इसे अधिक जटिल बनाया जा सके।
    छह। इंटरनेट पर दर्जनों और सैकड़ों झूठे एन्क्रिप्टेड संदेश बनाएं।
    सात। किसी भी इंटरनेट-कनेक्टेड डिवाइस पर मूल्य अनुक्रम को न सहेजें, यदि आप ऐसा करते हैं तो वास्तविक मूल्य न रखें, ऐसा मूल्य रखें जिसमें आपको अपने जन्मदिन का दिन और महीना जोड़ना हो या कुछ ऐसा जो आपको याद रखना आसान हो।
    आठ। इंटरनेट से कनेक्ट होने वाले डिवाइस पर मूल टेक्स्ट की कॉपी और पेस्ट न करें क्योंकि यह RAM में संग्रहीत हो जाता है। केवल तब कॉपी और पेस्ट का उपयोग करें जब टेक्स्ट एन्क्रिप्टेड हो।
                """,                            
                "Français": """
    1. Utilisez l'application sur un appareil hors ligne comme Raspberry Pi, Orange Pi Plus, ...
    2. Effectuez un déchiffrement avec mot de passe, le cas échéant, pour vérifier que le chiffrement a été effectué correctement.
    3. Créez vos propres modèles, ajoutez l'espace représenté par "␣" pour que tout le contenu soit chiffré et collez de nouveaux caractères qui ne sont pas dans la liste des langues pour ajouter de nouveaux caractères.
    4. Créez des chiffrements multiples avec mot de passe et différents modèles en sautant entre les langues.
    5. Convenez en personne du premier chiffrement pour le rendre plus complexe en donnant des instructions dans le message chiffré.
    6. Créez des dizaines et des centaines de faux messages chiffrés circulant sur Internet.
    7. Ne sauvegardez pas la séquence de valeurs sur un appareil connecté à Internet, si vous le faites, ne mettez pas la vraie valeur, mettez une valeur à laquelle vous devez ajouter votre jour et mois de naissance ou quelque chose de similaire qui soit facile à retenir.
    8. Ne copiez et collez pas de texte original sur un appareil connecté à Internet car il est stocké dans la RAM. Utilisez le copier-coller uniquement lorsque le texte est crypté.
                """,
                "عربي": """
    استخدم التطبيق على جهاز غير متصل بالإنترنت مثل Raspberry Pi, Orange Pi Plus,...
    ٢. قم بفك التشفير باستخدام كلمة المرور إذا كانت موجودة للتحقق من أن التشفير تم بشكل صحيح.
    ٣. قم بإنشاء قوالبك الخاصة، وأضف المسافة ممثلة بـ "␣" لضمان تشفير كل المحتوى، والصق أحرفًا جديدة غير موجودة في قائمة اللغات لإضافة أحرف جديدة.
    ٤. قم بإنشاء تشفيرات متعددة بكلمة مرور وقوالب مختلفة مع القفز بين اللغات.
    ٥. اتفق شخصيًا على التشفير الأول لجعله أكثر تعقيدًا من خلال إعطاء تعليمات في الرسالة المشفرة.
    ٦. قم بإنشاء عشرات ومئات من الرسائل المشفرة الزائفة المنتشرة على الإنترنت.
    ٧. لا تحفظ تسلسل القيم على أي جهاز متصل بالإنترنت، إذا فعلت ذلك فلا تضع القيمة الحقيقية، ضع قيمة يجب عليك إضافة يوم وشهر ميلادك إليها أو شيء مماثل يسهل عليك تذكره.
    لا تستخدم النسخ واللصق للنص الأصلي على جهاز يتصل بالإنترنت لأنه يتم تخزينه في ذاكرة الوصول العشوائي. استخدم النسخ واللصق فقط عندما يكون النص مشفرًا.
                """,
                "বাংলা": """
    ১. ইন্টারনেট সংযোগহীন ডিভাইসে অ্যাপ্লিকেশনটি ব্যবহার করুন যেমন Raspberry Pi, Orange Pi Plus,...
    ২. এনক্রিপশন সঠিকভাবে সম্পন্ন হয়েছে কিনা তা যাচাই করার জন্য পাসওয়ার্ড দিয়ে ডিক্রিপশন করুন, যদি থাকে।
    ৩. আপনার নিজস্ব টেমপ্লেট তৈরি করুন, স্পেস "␣" হিসাবে প্রতিনিধিত্ব করে যোগ করুন যাতে সমস্ত বিষয়বস্তু এনক্রিপ্ট হয় এবং নতুন অক্ষর যোগ করতে ভাষার তালিকায় নেই এমন নতুন অক্ষর পেস্ট করুন।
    ৪. পাসওয়ার্ড এবং বিভিন্ন টেমপ্লেট দিয়ে একাধিক এনক্রিপশন তৈরি করুন, ভাষাগুলির মধ্যে লাফিয়ে।
    ৫. এনক্রিপ্টেড বার্তায় নির্দেশনা দিয়ে এটিকে আরও জটিল করার জন্য ব্যক্তিগতভাবে প্রথম এনক্রিপশন সম্মত করুন।
    ৬. ইন্টারনেটে ঘুরে বেড়ানো ডজন ডজন এবং শত শত ভুয়া এনক্রিপ্টেড বার্তা তৈরি করুন।
    ৭. কোনও ইন্টারনেট-সংযুক্ত ডিভাইসে মান ক্রম সংরক্ষণ করবেন না, যদি আপনি তা করেন তবে আসল মানটি রাখবেন না, এমন একটি মান রাখুন যাতে আপনাকে আপনার জন্মদিনের দিন এবং মাস যোগ করতে হবে বা এই ধরনের কিছু যা আপনার পক্ষে মনে রাখা সহজ।
    আট ইন্টারনেটের সাথে সংযুক্ত ডিভাইসে মূল পাঠ্যের কপি এবং পেস্ট করবেন না কারণ এটি RAM-এ সঞ্চিত হয়। শুধুমাত্র তখনই কপি এবং পেস্ট ব্যবহার করুন যখন পাঠ্যটি এনক্রিপ্ট করা থাকে।
                """,
                "Русский": """
    1. Используйте приложение на устройстве без подключения к Интернету, например Raspberry Pi, Orange Pi Plus,...
    2. Выполните расшифровку с паролем, если он есть, чтобы проверить правильность выполнения шифрования.
    3. Создайте свои собственные шаблоны, добавьте пробел, представленный как "␣", чтобы зашифровать весь контент, и вставьте новые символы, которых нет в списке языков, чтобы добавить новые символы.
    4. Создавайте множественные шифрования с паролем и разными шаблонами, переходя между языками.
    5. Согласуйте лично первое шифрование, чтобы сделать его более сложным, давая инструкции в зашифрованном сообщении.
    6. Создайте десятки и сотни ложных зашифрованных сообщений, циркулирующих в Интернете.
    7. Не сохраняйте последовательность значений на устройстве, подключенном к Интернету, если вы это делаете, не ставьте реальное значение, поставьте значение, к которому вам нужно добавить день и месяц вашего рождения или что-то подобное, что вам легко запомнить.
    8. Не копируйте и не вставляйте оригинальный текст на устройство, подключенное к Интернету, так как он сохраняется в оперативной памяти. Используйте копирование и вставку только тогда, когда текст зашифрован.
                """,
                "Português": """
    1. Use o aplicativo em um dispositivo offline, como Raspberry Pi, Orange Pi Plus, ...
    2. Realize uma descriptografia com senha, se houver, para verificar se a criptografia foi realizada corretamente.
    3. Crie seus próprios modelos, adicione o espaço representado como "␣" para que todo o conteúdo seja criptografado e cole novos caracteres que não estejam na lista de idiomas para adicionar novos caracteres.
    4. Crie múltiplas criptografias com senha e diferentes modelos, saltando entre idiomas.
    5. Concorde pessoalmente sobre a primeira criptografia para torná-la mais complexa, dando instruções na mensagem criptografada.
    6. Crie dezenas e centenas de mensagens criptografadas falsas circulando pela Internet.
    7. Não salve a sequência de valores em nenhum dispositivo conectado à Internet, se o fizer, não coloque o valor real, coloque um valor ao qual você precisa adicionar o dia e mês do seu aniversário ou algo semelhante que seja fácil de lembrar.
    8. Não copie e cole texto original em um dispositivo que se conecta à Internet, pois ele fica armazenado na RAM. Use copiar e colar apenas quando o texto estiver criptografado.
                """,
                "Deutsch": """
    1. Verwenden Sie die Anwendung auf einem Offline-Gerät wie Raspberry Pi, Orange Pi Plus, ...
    2. Führen Sie eine Entschlüsselung mit Passwort durch, falls vorhanden, um zu überprüfen, ob die Verschlüsselung korrekt durchgeführt wurde.
    3. Erstellen Sie Ihre eigenen Vorlagen, fügen Sie das als "␣" dargestellte Leerzeichen hinzu, damit der gesamte Inhalt verschlüsselt wird, und fügen Sie neue Zeichen ein, die nicht in der Sprachenliste enthalten sind, um neue Zeichen hinzuzufügen.
    4. Erstellen Sie mehrfache Verschlüsselungen mit Passwort und verschiedenen Vorlagen, indem Sie zwischen den Sprachen wechseln.
    5. Vereinbaren Sie die erste Verschlüsselung persönlich, um sie komplexer zu gestalten, indem Sie Anweisungen in der verschlüsselten Nachricht geben.
    6. Erstellen Sie Dutzende und Hunderte von falschen verschlüsselten Nachrichten, die im Internet kursieren.
    7. Speichern Sie die Wertesequenz nicht auf einem internetfähigen Gerät. Wenn Sie es doch tun, geben Sie nicht den echten Wert an, sondern einen Wert, zu dem Sie Ihren Geburtstag und -monat addieren müssen oder etwas Ähnliches, das Sie sich leicht merken können.
    8. Kopieren und fügen Sie keinen Originaltext auf einem Gerät ein, das mit dem Internet verbunden ist, da er im RAM gespeichert wird. Verwenden Sie Kopieren und Einfügen nur, wenn der Text verschlüsselt ist.
                """,
                "日本語": """
    1つ。Raspberry Pi、Orange Pi Plus などのオフラインデバイスでアプリケーションを使用してください。
    二。 パスワードがある場合は、暗号化が正しく行われたことを確認するためにパスワードで復号化を行ってください。
    三つ。独自のテンプレートを作成し、すべてのコンテンツが暗号化されるようにスペースを"␣"として表現し、新しい文字を追加するために言語リストにない新しい文字を貼り付けてください。
    四。パスワードと異なるテンプレートを使用して、言語間をジャンプしながら複数の暗号化を作成してください。
    五。暗号化されたメッセージで指示を与えることで、最初の暗号化をより複雑にするために個人的に同意してください。
    六。インターネット上で流通する偽の暗号化メッセージを数十、数百作成してください。
    セブン。インターネットに接続されたデバイスに値のシーケンスを保存しないでください。もし保存する場合は、実際の値を置かず、あなたの誕生日の日と月を足さなければならない値や、覚えやすい類似のものを置いてください。
    八。インターネットに接続されているデバイスで元のテキストをコピー＆ペーストしないでください。RAM に保存されます。テキストが暗号化されている場合にのみ、コピー＆ペーストを使用してください。
                """,
                "Türkçe": """
    1. Uygulamayı Raspberry Pi, Orange Pi Plus gibi internete bağlı olmayan bir cihazda kullanın,...
    2. Şifrelemenin doğru yapıldığını kontrol etmek için varsa şifre ile şifre çözme işlemi yapın.
    3. Kendi şablonlarınızı oluşturun, tüm içeriğin şifrelenmesi için boşluğu "␣" olarak temsil eden karakteri ekleyin ve yeni karakterler eklemek için dil listesinde olmayan yeni karakterleri yapıştırın.
    4. Şifre ve farklı şablonlarla, diller arasında atlayarak çoklu şifrelemeler oluşturun.
    5. İlk şifrelemeyi daha karmaşık hale getirmek için şifreli mesajda talimatlar vererek yüz yüze anlaşın.
    6. İnternette dolaşan düzinelerce ve yüzlerce sahte şifreli mesaj oluşturun.
    7. Değer dizisini internet bağlantılı herhangi bir cihazda saklamayın, eğer saklarsanız gerçek değeri koymayın, doğum gününüzün gün ve ayını eklemeniz gereken bir değer veya hatırlaması kolay benzer bir şey koyun.
    8. Orijinal metni internete bağlanan bir cihazda kopyalayıp yapıştırmayın çünkü RAM'de saklanır. Yalnızca metin şifreli olduğunda kopyala ve yapıştır kullanın.
                """,
                "한국어": """
    하나 Raspberry Pi, Orange Pi Plus와 같은 인터넷에 연결되지 않은 장치에서 애플리케이션을 사용하십시오,...
    둘 암호화가 올바르게 수행되었는지 확인하기 위해 비밀번호가 있는 경우 비밀번호로 복호화를 수행하세요.
    삼 자신만의 템플릿을 만들고, 모든 내용이 암호화되도록 공백을 "␣"로 표시하며, 새로운 문자를 추가하기 위해 언어 목록에 없는 새로운 문자를 붙여넣으세요.
    네 비밀번호와 다양한 템플릿을 사용하여 언어 간에 전환하면서 다중 암호화를 만드세요.
    다섯 암호화된 메시지에 지시사항을 제공하여 첫 번째 암호화를 더 복잡하게 만들기 위해 직접 합의하세요.
    육 인터넷상에서 유포되는 수십, 수백 개의 가짜 암호화 메시지를 만드세요.
    일곱 인터넷에 연결된 기기에 값 시퀀스를 저장하지 마세요. 만약 저장한다면 실제 값을 넣지 말고, 생일의 날짜와 월을 더해야 하는 값이나 기억하기 쉬운 유사한 것을 넣으세요.
    여덟 인터넷에 연결된 장치에서 원본 텍스트를 복사하여 붙여넣지 마십시오. RAM에 저장되기 때문입니다. 텍스트가 암호화된 경우에만 복사 및 붙여넣기를 사용하십시오.
        """,
        }
        self.creditos_texto = {
                "Español": """
            LIVENCRYPT
            Desarrollado por Synergia86
            Versión: 1.1
            Año: 2024
    
            La intención de crear LIVENCRYPT es por un bien en la seguridad de los políticos, banqueros y filántropos eugenistas. Son los verdaderos motores de la economía y sus mensajes deben de estar cifrados para que la HUMANIDAD no descubra la gran estafa de vida que nos están creando en la realidad que compartimos. Nos crean problemas para eliminarnos la privacidad a cambio de una falsa seguridad y siempre tras una frase mágica; "Todo lo hacen por nuestro bien". Con esta aplicación difícilmente cambiará la realidad que compartimos, pero sí será un grano de arena en el ojo que todo lo ve y con la suma de la HUMANIDAD acabarán ciegos. Si has llegado hasta aquí ten por seguro que no es por casualidad, sino por causalidad, vamos a dejar una buena huella en el camino y compartamos la aplicación con más SERES HUMANOS para que los algoritmos de la IA en predecir escenarios comiencen a fallar estrepitosamente.
    
            Únete a la comunidad
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
    
            Donaciones
            Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
            Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
                """,
                "English": """
            LIVENCRYPT
            Developed by Synergia86
            Version: 1.1
            Year: 2024
    
            The intention behind creating LIVENCRYPT is for the sake of the security of politicians, bankers, and eugenicist philanthropists. They are the true drivers of the economy, and their messages must be encrypted so that HUMANITY does not discover the great life scam that they are creating in the reality we share. They create problems to take away our privacy in exchange for false security, always behind a magic phrase; "Everything they do is for our own good." This application will hardly change the reality we share, but it will be a grain of sand in the eye that sees everything, and with the sum of HUMANITY, they will end up blind. If you have reached this point, rest assured it is not by chance, but by causality. Let’s leave a good mark on the path and share the application with more HUMAN BEINGS so that the AI algorithms predicting scenarios begin to fail spectacularly.
    
            Join the community
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
    
            Donations
            Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
            Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
                """,
                "中文":  """
            LIVENCRYPT
            由 Synergia86 开发
            版本：一.零
            年份：四七二二
    
            的目的是为了政客、银行家和优生学慈善家的安全。他们是经济的真正驱动力，他们的信息必须加密，以防止人类发现他们在我们共享的现实中制造的巨大生活骗局。他们制造问题，剥夺我们的隐私，以换取虚假的安全，并总是用一句魔法般的话来掩饰；“一切都是为了我们的利益”。这个应用程序难以改变我们共享的现实，但它将成为那只全视之眼中的一粒沙子，并随着人类的总和，最终使其失明。如果你已经走到这里，请相信这不是偶然，而是因果。让我们在道路上留下一个好的印记，并与更多的人类分享这个应用程序，以便预测场景的人工智能算法开始大幅度失败。
    
            加入社区
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
        
            捐赠
            以太坊 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
            日光浴室 FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            比特幣 bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            門羅幣 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
                """,
                "हिन्दी": """
            LIVENCRYPT
            Synergia86 द्वारा विकसित
            संस्करण: एक.शून्य
            वर्ष: दो हजार चौबीस
            
            LIVENCRYPT बनाने का इरादा राजनीतिज्ञों, बैंकरों और यूजेनिक परोपकारियों की सुरक्षा के लिए है। वे अर्थव्यवस्था के वास्तविक चालक हैं और उनके संदेशों को एन्क्रिप्ट किया जाना चाहिए ताकि मानवता हमारे साझा किए गए वास्तविकता में वे जो बड़ा जीवन घोटाला कर रहे हैं, उसे न खोज सके। वे समस्याएँ पैदा करते हैं ताकि हमारी निजता को समाप्त किया जा सके और बदले में एक झूठी सुरक्षा दी जा सके, और हमेशा एक जादुई वाक्यांश के पीछे; "वे सब कुछ हमारे भले के लिए करते हैं"। इस एप्लिकेशन से हमारे साझा किए गए वास्तविकता को बदलना मुश्किल है, लेकिन यह सब कुछ देखने वाली आँख में एक रेत का कण होगा और मानवता के योग से वे अंधे हो जाएंगे। यदि आप यहाँ तक पहुँचे हैं, तो निश्चित मानें कि यह संयोग नहीं बल्कि कारणवश है। चलिए रास्ते में एक अच्छा निशान छोड़ते हैं और इस एप्लिकेशन को और अधिक मानव प्राणियों के साथ साझा करते हैं ताकि परिदृश्यों की भविष्यवाणी करने वाले एआई एल्गोरिदम बुरी तरह से विफल होना शुरू करें।
            
            समुदाय में शामिल हों
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
            
            दान
            एथेरियम 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71 
            धूपघड़ी FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            बीटीसी bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn 
            मोनेरो 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
                """,
                "Français": """
            LIVENCRYPT
            Développé par Synergia86
            Version : 1.0
            Année : 2024
    
            L'intention de créer LIVENCRYPT est pour le bien de la sécurité des politiciens, des banquiers et des philanthropes eugénistes. Ils sont les véritables moteurs de l'économie et leurs messages doivent être chiffrés pour que l'HUMANITÉ ne découvre pas la grande escroquerie de la vie qu'ils créent dans la réalité que nous partageons. Ils créent des problèmes pour éliminer notre vie privée en échange d'une fausse sécurité et toujours derrière une phrase magique : "Tout ce qu'ils font, c'est pour notre bien". Cette application ne changera guère la réalité que nous partageons, mais elle sera un grain de sable dans l'œil qui voit tout et avec la somme de l'HUMANITÉ, ils finiront aveugles. Si vous êtes arrivé jusqu'ici, soyez sûr que ce n'est pas par hasard, mais par causalité, nous allons laisser une bonne empreinte sur le chemin et partager l'application avec plus d'ÊTRES HUMAINS pour que les algorithmes de l'IA pour prédire les scénarios commencent à échouer de manière spectaculaire.
    
            Rejoignez la communauté
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
    
            Dons
            Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
            Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
                """,
                "عربي":  """
            LIVENCRYPT
            تم تطويره بواسطة Synergia86 
            الإصدار: ١.٠
            السنة: ١٤٤٥
            
            إن نية إنشاء LIVENCRYPT هي لصالح أمن السياسيين والمصرفيين والمحسنين الذين يؤمنون بتحسين النسل. إنهم المحركات الحقيقية للاقتصاد ويجب تشفير رسائلهم لكي لا تكتشف الإنسانية الخدعة الكبرى التي يخلقونها لنا في الواقع الذي نشاركه. إنهم يخلقون مشاكل لإزالة خصوصيتنا مقابل أمان زائف ودائماً وراء عبارة سحرية؛ "كل ما يفعلونه هو من أجل مصلحتنا". من الصعب أن يغير هذا التطبيق الواقع الذي نشاركه، لكنه سيكون حبة رمل في العين التي ترى كل شيء ومع مجموع الإنسانية سيصبحون عميان. إذا وصلت إلى هنا فتأكد أن هذا ليس صدفة، بل هو نتيجة، دعونا نترك أثراً جيداً في الطريق ونشارك التطبيق مع المزيد من البشر لكي تبدأ خوارزميات الذكاء الاصطناعي في التنبؤ بالسيناريوهات بالفشل الذريع.
    
        انضم إلى المجتمع
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
    
        التبرعات
            0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71  سولانا 
            FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn  إيثريوم   
            bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn   بيتكوين
            47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g  مونيرو
                """,
                "বাংলা":  """
            LIVENCRYPT
            Synergia86 দ্বারা উন্নত
            সংস্করণ: ১.০
            বছর: ২০২৪
    
            LIVENCRYPT তৈরি করার উদ্দেশ্য হলো রাজনৈতিক নেতা, ব্যাংকার এবং ইউজেনিস্ট দাতাদের নিরাপত্তার জন্য। তারা অর্থনীতির প্রকৃত চালক এবং তাদের বার্তাগুলি এনক্রিপ্ট করা উচিত যাতে মানবতা তাদের তৈরি করা জীবনের বড় প্রতারণা আমাদের ভাগ করা বাস্তবতায় আবিষ্কার না করে। তারা আমাদের গোপনীয়তা মুছে ফেলার জন্য সমস্যা সৃষ্টি করে, একটি মিথ্যা নিরাপত্তার বিনিময়ে, এবং সবসময় একটি জাদুকরী বাক্যের পিছনে; "তারা সবকিছু আমাদের ভালোর জন্য করে"। এই অ্যাপ্লিকেশনটি আমাদের ভাগ করা বাস্তবতাকে সহজে পরিবর্তন করবে না, কিন্তু এটি সবকিছু দেখার চোখে একটি বালির দানা হবে এবং মানবতার যোগফল দিয়ে তারা অন্ধ হয়ে যাবে। আপনি যদি এখানে পৌঁছান, তবে নিশ্চিত হোন এটি কাকতালীয় নয়, বরং কারণস্বরূপ। আসুন আমরা পথে একটি ভালো চিহ্ন রেখে যাই এবং আরও মানব সত্তার সাথে এই অ্যাপ্লিকেশনটি শেয়ার করি যাতে AI-এর অ্যালগরিদমগুলি ভবিষ্যদ্বাণী করতে ব্যর্থ হতে শুরু করে।
    
            সম্প্রদায়ে যোগদান করুন
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
    
            দান
            ইথেরিয়াম 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
            সোলানা FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            বিটকয়েন bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            মোনেরো 42Bm675ZUHw96vXdiRYCkhdyRzS6ySbPed3CLh5zR5g1CQqQbqT8LU6gaRQ6eVxdS8JKPUfyYTZV3G111DyJzFwJKVPfNJ
    
                """,
                "Русский":  """
            LIVENCRYPT
            Разработано Synergia86
            Версия: 1.1
            Год: 2024
    
            Цель создания LIVENCRYPT заключается в обеспечении безопасности политиков, банкиров и эугеника-филантропов. Они являются истинными двигателями экономики, и их сообщения должны быть зашифрованы, чтобы ЧЕЛОВЕЧЕСТВО не узнало о великой жизненной афере, которую они создают в реальности, которую мы разделяем. Они создают проблемы, чтобы лишить нас конфиденциальности в обмен на ложную безопасность, всегда под прикрытием магической фразы: «Они делают всё для нашего блага». Это приложение вряд ли изменит реальность, которую мы разделяем, но оно будет песчинкой в глазу, который видит всё, и с накоплением ЧЕЛОВЕЧЕСТВА они станут слепыми. Если вы дошли до этого места, будьте уверены, что это не случайность, а необходимость. Давайте оставим хороший след на пути и поделимся этим приложением с большим количеством ЛЮДЕЙ, чтобы алгоритмы ИИ по прогнозированию сценариев начали катастрофически ошибаться.
    
            Присоединяйтесь к сообществу
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
    
    
            Пожертвования
            Эфириум 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
            Солана FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            Биткойн bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            Эфириум 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
                """,
                "Português":  """
            LIVENCRYPT
            Desenvolvido por Synergia86
            Versão: 1.1
            Ano: 2024
    
            A intenção de criar o LIVENCRYPT é para o bem da segurança dos políticos, banqueiros e filantropos eugênicos. Eles são os verdadeiros motores da economia e suas mensagens devem estar criptografadas para que a HUMANIDADE não descubra a grande fraude de vida que estão criando na realidade que compartilhamos. Eles criam problemas para remover nossa privacidade em troca de uma falsa segurança, sempre com uma frase mágica; "Tudo o que fazem é para o nosso bem". Este aplicativo dificilmente mudará a realidade que compartilhamos, mas será um grão de areia no olho que tudo vê e, com a soma da HUMANIDADE, eles acabarão cegos. Se você chegou até aqui, tenha certeza de que não é por acaso, mas por causalidade. Vamos deixar uma boa marca no caminho e compartilhar o aplicativo com mais SERES HUMANOS para que os algoritmos de IA para prever cenários comecem a falhar estrepitosamente.
    
            Junte-se à comunidade
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
    
            Doações
            Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
            Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
                """,
                "Deutsch": """
            LIVENCRYPT
            Entwickelt von Synergia86
            Version: 1.1
            Jahr: 2024
    
            Die Absicht, LIVENCRYPT zu erstellen, besteht darin, die Sicherheit von Politikern, Bankern und eugenischen Philanthropen zu gewährleisten. Sie sind die wahren Treiber der Wirtschaft, und ihre Nachrichten müssen verschlüsselt werden, damit die MENSCHHEIT nicht die große Lebenslüge entdeckt, die sie in der Realität erschaffen, die wir teilen. Sie schaffen Probleme, um unsere Privatsphäre gegen eine falsche Sicherheit auszutauschen, immer hinter einem magischen Satz: "Alles, was sie tun, ist zu unserem Wohl". Diese Anwendung wird die Realität, die wir teilen, kaum ändern, aber sie wird ein Sandkorn im Auge sein, das alles sieht, und mit der Summe der MENSCHHEIT werden sie blind werden. Wenn du bis hierher gekommen bist, sei dir sicher, dass es nicht zufällig, sondern kausal ist. Lass uns einen guten Eindruck auf dem Weg hinterlassen und die Anwendung mit mehr MENSCHEN teilen, damit die KI-Algorithmen zur Szenarienvorhersage anfangen, spektakulär zu scheitern.
    
            Tritt der Gemeinschaft bei
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
            
            Spenden
            Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
            Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
                """,
                "日本語": """
            LIVENCRYPT
            Synergia86によって開発されました
            バージョン: 1.1
            年: 令和6年
    
            LIVENCRYPTを作成する意図は、政治家、銀行家、そして優生主義の慈善家たちの安全のためです。彼らは経済の真の駆動力であり、彼らのメッセージは暗号化されるべきです。そうしないと、人類が彼らが共有している現実の中で作り出している大規模な人生の詐欺を発見することになります。彼らは、虚偽の安全を交換条件に私たちのプライバシーを奪う問題を作り出し、常に魔法のようなフレーズの後ろに隠れています。「彼らがするすべては私たちのために」です。このアプリケーションが共有している現実を変えることは難しいですが、それはすべてを見通す目の中の一粒の砂となり、人類の総体とともに彼らは盲目になるでしょう。ここまで来たなら、これは偶然ではなく必然であることを確信してください。私たちは道に良い痕跡を残し、より多くの人間とこのアプリケーションを共有して、AIアルゴリズムがシナリオ予測に失敗し始めるようにしましょう。
    
            コミュニティに参加する
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
        
            寄付
            イーサリアム 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
            ソラナ FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            ビットコイン bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            モネロ 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
    
                """,
                "Türkçe": """
            LIVENCRYPT
            Synergia86 tarafından geliştirildi
            Sürüm: 1.1
            Yıl: 1445
    
            LIVENCRYPT oluşturmanın amacı, politikacıların, bankacıların ve eugenik hayırseverlerin güvenliğine katkıda bulunmaktır. Onlar ekonominin gerçek motorlarıdır ve mesajlarının şifrelenmesi gerekmektedir, böylece İNSANLIK onların paylaştığımız gerçeklikte yarattıkları büyük yaşam dolandırıcılığını keşfedemez. Bizim gizliliğimizi sahte bir güvenlik karşılığında ortadan kaldırmak için sorunlar yaratırlar ve her zaman sihirli bir cümlenin arkasında gizlenirler: "Her şeyi bizim iyiliğimiz için yaparlar." Bu uygulama, paylaştığımız gerçekliği değiştirmek zor olacaktır, ancak her şeyi gören gözde bir kum tanesi olacak ve İNSANLIK toplamı ile kör olacaklardır. Buraya kadar geldiyseniz, bunun tesadüf değil, zorunluluk olduğunu bilmelisiniz. Yolda iyi bir iz bırakacağız ve bu uygulamayı daha fazla İNSANLA paylaşarak, yapay zekâ algoritmalarının senaryo tahminlerinde büyük bir başarısızlık yaşamalarını sağlayacağız.
    
            Topluluğa katılın
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
    
            Bağışlar
            ETH 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71
            Solana FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            Bitcoin bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            Monero 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
                """,
                "한국어": """
            LIVENCRYPT
            Synergia86에 의해 개발됨
            버전: 1.1
            연도: 백십삼
    
            LIVENCRYPT를 만들려는 의도는 정치인, 은행가, 그리고 우생학 자선가들의 안전을 위한 것입니다. 그들은 경제의 진정한 원동력이며, 그들의 메시지는 암호화되어야 합니다. 그렇지 않으면 인류가 우리가 공유하는 현실에서 그들이 만들어낸 큰 인생 사기를 발견하게 됩니다. 그들은 우리의 사생활을 없애기 위해 문제를 만들어내고, 거짓된 안전을 대가로 하고, 항상 마법 같은 문구 뒤에 숨겨져 있습니다: "모든 것은 우리의 이익을 위해서입니다." 이 애플리케이션이 우리가 공유하는 현실을 바꾸기는 어렵겠지만, 모든 것을 보는 눈에 한 알의 모래가 될 것이며, 인류의 총합으로 인해 그들은 눈이 멀게 될 것입니다. 여기에 도달했다면 우연이 아니라 필연이라고 확신하세요. 우리는 길에 좋은 흔적을 남기고, 더 많은 인류와 이 애플리케이션을 공유하여 AI 알고리즘이 시나리오 예측에서 크게 실패하기 시작하도록 합시다.
    
            커뮤니티에 참여하세요
            https://discord.gg/sDRawvyXhy
            x.com/Livencrypt1
            github.com/Synergia86
            gitee.com/Synergia_0ef4
    
            기부
            이더리움 0xb3979A96A5B36e83e6bc01203c556Fa467a7Be71 
            솔라나 FC766e5UR9nicjkLWYa9gCiYnYWKmrKBNyDfWnT2qLGn
            비트코인 bc1quf92f38wjfd36d9uxtu6x23d2sakfjn6r4j7cn
            모네로 47nbMBmvwTk9Rq9KaRZEHARPJoB3Xpj4ycrSChz5GyFcQpfXYXa5ifXV7yJixGcGz72GAn9zWbr7iLSUj6XMtAxn2EfWL3g
        """,
        } 
        self.licencia_texto = {
                "Español": """
        Licencia Pública General de GNU
        
                Versión 3, 29 de junio de 2007
                
                Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
                Todos los derechos reservados.
                
                Preamble
                
                La Licencia Pública General de GNU es una licencia libre, diseñada para garantizar la libertad de compartir y modificar software. Esta licencia permite a los usuarios la libertad de usar, estudiar, compartir (copiar) y modificar el software.
                
                Términos y Condiciones para la Copia, Distribución y Modificación
                
                0. Definiciones.
                
                "Este Licenciante" se refiere a la persona o entidad que originalmente distribuye el Trabajo bajo esta Licencia.
                
                "Usted" se refiere a cualquier persona que ejerza derechos bajo esta Licencia, ya sea que haya recibido o no el Trabajo directamente del Licenciante.
                
                "Trabajo" se refiere al material protegido por derechos de autor que está sujeto a esta Licencia.
                
                "Obra Derivada" se refiere a cualquier trabajo bajo derechos de autor, incluyendo el Trabajo y modificaciones del mismo, preparado bajo esta Licencia.
                
                "Texto de la Licencia" se refiere al texto enunciado en esta Licencia.
                
                "Aplicación" se refiere a cualquier trabajo en el cual el Trabajo o cualquier obra derivada de este se haya transformado de tal manera que el Trabajo o la obra derivada contenga únicamente una porción representativa de la misma.
                
                "Objeto Código Ejecutable" se refiere al Objeto Código ejecutable generado a partir del Trabajo.
                
                1. Concesión de Licencia.
                
                Sujeto a los términos y condiciones de esta Licencia, cada licenciante le otorga a usted una licencia no exclusiva, mundial y perpetua para copiar, modificar, realizar y distribuir el Trabajo, así como para hacer y distribuir obras derivadas del mismo, siempre que cumpla con lo siguiente:
                
                A. La fuente del Trabajo debe acompañarse con una copia de esta Licencia. Si el Trabajo y las obras derivadas se distribuyen en formato de objeto código ejecutable, el texto de esta Licencia debe incluirse en una forma fácilmente legible en la documentación asociada con la distribución, utilizando al menos caracteres de tamaño de fuente normal.
                
                B. Las modificaciones introducidas por usted deben ser significativas y, en conjunto, representen un cambio sustancial en el Trabajo.
                
                C. Las obras derivadas deben estar bajo los términos de esta Licencia.
                
                D. Si el Trabajo incluye un aviso de derechos de autor y/o otros avisos legales que se refieran a la licencia, debe conservar estos avisos en todos los ejemplares que usted haga del Trabajo o las obras derivadas.
                
                E. No puede imponer términos adicionales, ni aplicar ninguna medida tecnológica que restrinja legalmente a otros de ejercer las libertades otorgadas por esta Licencia.
                
                2. Condiciones adicionales.
                
                Usted no está autorizado a copiar, modificar, sublicenciar o distribuir el Trabajo, excepto según lo expresamente dispuesto en esta Licencia. Cualquier intento de copia, modificación, sublicenciamiento o distribución no autorizados invalidará automáticamente su derecho a ejercer derechos bajo esta Licencia.
                
                3. Revocación automática de la Licencia.
                
                Usted no puede ejercer sus derechos bajo esta Licencia si no cumple con todos los términos y condiciones de esta Licencia. Si se viola cualquier término o condición de esta Licencia, sus derechos se revocarán automáticamente.
                
                4. Exención de Responsabilidad.
                
                EXCEPTO LO EXPLICITAMENTE ESTABLECIDO EN ESTA LICENCIA, EL TRABAJO SE PROPORCIONA "TAL CUAL", SIN GARANTÍAS O CONDICIONES DE NINGÚN TIPO, YA SEAN EXPRESAS O IMPLÍCITAS, INCLUYENDO, PERO NO LIMITÁNDOSE A, GARANTÍAS O CONDICIONES DE TÍTULO O NO INFRACCIÓN, O GARANTÍAS O CONDICIONES IMPLÍCITAS DE COMERCIABILIDAD O ADECUACIÓN PARA UN PROPÓSITO PARTICULAR. USTED ASUME LA RESPONSABILIDAD EXCLUSIVA DE LA SELECCIÓN DEL TRABAJO PARA LOGRAR SUS RESULTADOS DESEADOS Y DE LA INSTALACIÓN, USO Y RESULTADOS OBTENIDOS DEL TRABAJO.
                
                5. Limitación de Responsabilidad.
                
                EN NINGÚN CASO EL LICENCIANTE SERÁ RESPONSABLE ANTE USTED POR DAÑOS, INCLUYENDO CUALQUIER TIPO DE DAÑOS INDIRECTOS, ESPECIALES, INCIDENTALES O CONSECUENTES ASOCIADOS CON EL TRABAJO O CON EL USO O DISTRIBUCIÓN DEL TRABAJO.
                
                El Texto de la Licencia
                
                El Texto de la Licencia para el proyecto LIVENCRYPT 1.1 se encuentra en múltiples idiomas.
                
                6. Variación de esta Licencia.
                
                La Fundación del Software Libre (FSF) puede publicar revisiones y/o versiones nuevas de la Licencia Pública General de GNU de vez en cuando. Dichas revisiones y/o versiones nuevas se aplicarán de manera prospectiva en el Trabajo publicado posteriormente bajo esta Licencia. La Fundación puede también publicar orientaciones adicionales para determinados programas de la FSF. Dichas orientaciones adicionales, si las hay, se considerarán parte de la Licencia Pública General de GNU a efectos de este Trabajo.
                
                Nota Final
                
                Esta es la Licencia Pública General de GNU que gobierna el Trabajo. Si no está de acuerdo con sus términos y condiciones, no tiene permiso para copiar, modificar, sublicenciar o distribuir el Trabajo excepto según lo expresamente dispuesto en esta Licencia. La distribución del Trabajo o de sus derivados implica la aceptación de estas condiciones.
        
                """,
                "English": """
        GNU General Public License
    
                Version 3, June 29, 2007
    
                Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
                All rights reserved.
    
                Preamble
    
                The GNU General Public License is a free license designed to ensure the freedom to share and modify software. This license allows users the freedom to use, study, share (copy), and modify the software.
    
                Terms and Conditions for Copying, Distribution, and Modification
    
                0. Definitions.
    
                "This Licensor" refers to the person or entity who originally distributes the Work under this License.
    
                "You" refers to any person who exercises rights under this License, whether or not they received the Work directly from the Licensor.
    
                "Work" refers to the copyrighted material that is subject to this License.
    
                "Derivative Work" refers to any work based on copyright, including the Work and modifications of it, prepared under this License.
    
                "License Text" refers to the text set forth in this License.
    
                "Application" refers to any work in which the Work or any Derivative Work has been transformed in such a way that the Work or Derivative Work contains only a representative portion of it.
    
                "Executable Object Code" refers to the executable object code generated from the Work.
    
                1. Grant of License.
    
                Subject to the terms and conditions of this License, each licensor grants you a non-exclusive, worldwide, perpetual license to copy, modify, perform, and distribute the Work, as well as to make and distribute Derivative Works of the Work, provided that you comply with the following:
    
                A. The source of the Work must be accompanied by a copy of this License. If the Work and Derivative Works are distributed in executable object code format, the text of this License must be included in a form that is easily readable in the documentation associated with the distribution, using at least normal font size characters.
    
                B. Modifications you make must be substantial and, taken together, represent a significant change to the Work.
    
                C. Derivative Works must be under the terms of this License.
    
                D. If the Work includes a copyright notice and/or other legal notices referring to the License, you must keep these notices in all copies of the Work or Derivative Works you make.
    
                E. You may not impose any additional terms, nor apply any technological measures that legally restrict others from exercising the freedoms granted by this License.
    
                2. Additional Conditions.
    
                You are not authorized to copy, modify, sublicense, or distribute the Work, except as expressly provided in this License. Any attempt to copy, modify, sublicense, or distribute the Work without authorization will automatically terminate your rights to exercise rights under this License.
    
                3. Automatic Revocation of the License.
    
                You may not exercise your rights under this License if you do not comply with all the terms and conditions of this License. If you violate any term or condition of this License, your rights will be automatically revoked.
    
                4. Disclaimer of Warranty.
    
                EXCEPT AS EXPRESSLY STATED IN THIS LICENSE, THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, WARRANTIES OR CONDITIONS OF TITLE OR NON-INFRINGEMENT, OR IMPLIED WARRANTIES OR CONDITIONS OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME THE ENTIRE RISK OF SELECTING THE WORK TO ACHIEVE YOUR INTENDED RESULTS AND FOR INSTALLATION, USE, AND RESULTS OBTAINED FROM THE WORK.
    
                5. Limitation of Liability.
    
                IN NO EVENT SHALL THE LICENSOR BE LIABLE TO YOU FOR ANY DAMAGES, INCLUDING ANY INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES RELATING TO THE WORK OR THE USE OR DISTRIBUTION OF THE WORK.
    
                License Text
    
                The License Text for the LIVENCRYPT 1.1 project is available in multiple languages.
    
                6. Variation of this License.
    
                The Free Software Foundation (FSF) may publish revisions and/or new versions of the GNU General Public License from time to time. Such revisions and/or new versions will apply prospectively to the Work published subsequently under this License. The Foundation may also publish additional guidelines for certain FSF programs. Such additional guidelines, if any, will be considered part of the GNU General Public License for this Work.
    
                Final Note
    
                This is the GNU General Public License governing the Work. If you do not agree to its terms and conditions, you do not have permission to copy, modify, sublicense, or distribute the Work except as expressly provided in this License. Distribution of the Work or its derivatives implies acceptance of these terms.
    
                """,
                "中文": """
            GNU通用公共许可证
    
                第三版，二〇〇七年六月二十九日
    
                版权 (C) 二〇〇七 自由软件基金会 <https://fsf.org/>
                保留所有权利。
    
                前言
    
                GNU通用公共许可证是一种自由许可证，旨在确保分享和修改软件的自由。此许可证允许用户自由使用、学习、分享（复制）和修改软件。
    
                复制、分发和修改的条款和条件
    
                0. 定义。
    
                “本许可方”是指最初根据本许可证分发作品的个人或实体。
    
                “您”是指任何根据本许可证行使权利的人，无论是否直接从许可方收到作品。
    
                “作品”是指受本许可证保护的版权材料。
    
                “衍生作品”是指在本许可证下准备的任何包含作品及其修改的受版权保护的作品。
    
                “许可证文本”是指本许可证中规定的文本。
    
                “应用程序”是指在其中作品或其任何衍生作品已被转换，以至于作品或衍生作品仅包含其代表性部分的任何作品。
    
                “可执行对象代码”是指从作品生成的可执行对象代码。
    
                1. 许可授予。
    
                根据本许可证的条款和条件，每个许可方授予您非独占、全球和永久的许可，以复制、修改、展示和分发作品，以及制作和分发其衍生作品，只要您遵守以下条件：
    
                A. 作品的源代码应附有本许可证的副本。如果作品及其衍生作品以可执行对象代码形式分发，本许可证的文本应以易读的形式包含在与分发相关的文档中，至少使用正常字体大小的字符。
    
                B. 您所做的修改必须是实质性的，并且总体上代表作品的实质性变化。
    
                C. 衍生作品必须遵守本许可证的条款。
    
                D. 如果作品包含版权声明和/或其他法律声明，您必须在您制作的作品或衍生作品的所有副本中保留这些声明。
    
                E. 您不得施加额外的条款，也不得实施任何技术措施，合法地限制他人行使本许可证所授予的自由。
    
                2. 附加条件。
    
                除非本许可证明确规定，您无权复制、修改、再许可或分发作品。任何未授权的复制、修改、再许可或分发将自动使您根据本许可证行使权利的权利失效。
    
                3. 自动撤销许可证。
    
                如果您未能遵守本许可证的所有条款和条件，您将不能行使本许可证下的权利。如果违反本许可证的任何条款或条件，您的权利将自动被撤销。
    
                4. 免责声明。
    
                除本许可证明确规定外，作品按“原样”提供，不提供任何形式的保证或条件，无论是明示还是默示的，包括但不限于所有权或不侵权的保证或条件，或适销性或适用于特定目的的默示保证或条件。您对选择作品以实现预期结果以及安装、使用和从作品中获得的结果承担全部责任。
    
                5. 责任限制。
    
                在任何情况下，许可方均不对您承担任何损害赔偿责任，包括与作品或使用或分发作品相关的任何间接、特殊、附带或后果性损害。
    
                许可证文本
    
                LIVENCRYPT 1.1 项目的许可证文本采用多种语言。
    
                6. 本许可证的变更。
    
                自由软件基金会 (FSF) 可能会不时发布修订和/或新版本的GNU通用公共许可证。此类修订和/或新版本将前瞻性地应用于之后根据本许可证发布的作品。基金会还可能为某些FSF程序发布额外的指导。这些额外的指导（如果有）将被视为本作品的GNU通用公共许可证的一部分。
    
                最后说明
    
                这是管理作品的GNU通用公共许可证。如果您不同意其条款和条件，则无权复制、修改、再许可或分发作品，除非本许可证明确规定。作品或其衍生作品的分发意味着接受这些条件。
    
                """,
                "हिन्दी": """
        GNU सार्वजनिक सामान्य लाइसेंस
    
                संस्करण 3, 29 जून 2007
    
                कॉपीराइट (C) 2007 फ्री सॉफ्टवेयर फाउंडेशन, इंक. <https://fsf.org/>
                सर्वाधिकार सुरक्षित।
    
                प्रस्तावना
    
                GNU सार्वजनिक सामान्य लाइसेंस एक मुफ्त लाइसेंस है, जिसे सॉफ़्टवेयर को साझा करने और संशोधित करने की स्वतंत्रता सुनिश्चित करने के लिए डिज़ाइन किया गया है। यह लाइसेंस उपयोगकर्ताओं को सॉफ़्टवेयर का उपयोग करने, अध्ययन करने, साझा (कॉपी) करने और संशोधित करने की स्वतंत्रता प्रदान करता है।
    
                प्रतिलिपि, वितरण और संशोधन के लिए शर्तें और नियम
    
                0. परिभाषाएँ।
    
                "यह लाइसेंसकर्ता" उस व्यक्ति या इकाई को संदर्भित करता है जो मूल रूप से इस लाइसेंस के तहत कार्य का वितरण करता है।
    
                "आप" किसी भी व्यक्ति को संदर्भित करता है जो इस लाइसेंस के तहत अधिकारों का प्रयोग करता है, चाहे उसने सीधे लाइसेंसकर्ता से कार्य प्राप्त किया हो या नहीं।
    
                "कार्य" उस कॉपीराइटेड सामग्री को संदर्भित करता है जो इस लाइसेंस के अधीन है।
    
                "व्युत्पन्न कार्य" किसी भी कॉपीराइटेड कार्य को संदर्भित करता है, जिसमें यह कार्य और इसके संशोधन शामिल हैं, जो इस लाइसेंस के तहत तैयार किए गए हैं।
    
                "लाइसेंस पाठ" इस लाइसेंस में उल्लिखित पाठ को संदर्भित करता है।
    
                "अनुप्रयोग" किसी भी कार्य को संदर्भित करता है जिसमें यह कार्य या इसका कोई व्युत्पन्न कार्य इस तरह से रूपांतरित हो गया हो कि कार्य या व्युत्पन्न कार्य केवल इसका प्रतिनिधि भाग ही शामिल हो।
    
                "क्रियान्वयन योग्य ऑब्जेक्ट कोड" उस क्रियान्वयन योग्य ऑब्जेक्ट कोड को संदर्भित करता है जो कार्य से उत्पन्न होता है।
    
                1. लाइसेंस का अनुदान।
    
                इस लाइसेंस की शर्तों और नियमों के अधीन, प्रत्येक लाइसेंसकर्ता आपको एक गैर-विशिष्ट, वैश्विक और स्थायी लाइसेंस प्रदान करता है ताकि आप कार्य को कॉपी, संशोधित, प्रदर्शन और वितरित कर सकें, साथ ही इसके व्युत्पन्न कार्य बना और वितरित कर सकें, बशर्ते कि आप निम्नलिखित का पालन करें:
    
                A. कार्य का स्रोत एक प्रतिलिपि इस लाइसेंस के साथ होना चाहिए। यदि कार्य और व्युत्पन्न कार्यों का वितरण क्रियान्वयन योग्य ऑब्जेक्ट कोड प्रारूप में किया जाता है, तो इस लाइसेंस का पाठ वितरण से संबंधित दस्तावेज़ में आसानी से पठनीय रूप में शामिल किया जाना चाहिए, जिसका उपयोग कम से कम सामान्य फॉन्ट आकार के अक्षरों का होना चाहिए।
    
                B. आपके द्वारा किए गए संशोधन महत्वपूर्ण होने चाहिए और सामूहिक रूप से कार्य में एक महत्वपूर्ण बदलाव का प्रतिनिधित्व करना चाहिए।
    
                C. व्युत्पन्न कार्यों को इस लाइसेंस की शर्तों के अधीन होना चाहिए।
    
                D. यदि कार्य में कॉपीराइट नोटिस और/या अन्य कानूनी नोटिस शामिल हैं जो लाइसेंस का संदर्भ देते हैं, तो आपको इन नोटिसों को सभी प्रतियों में रखना चाहिए जिन्हें आप कार्य या व्युत्पन्न कार्यों की बनाते हैं।
    
                E. आप अतिरिक्त शर्तें नहीं लगा सकते, न ही कोई तकनीकी उपाय लागू कर सकते हैं जो कानूनी रूप से दूसरों को इस लाइसेंस द्वारा प्रदान की गई स्वतंत्रता का प्रयोग करने से रोकता हो।
    
                2. अतिरिक्त शर्तें।
    
                आपको कार्य की प्रतिलिपि बनाने, संशोधित करने, सबलाइसेंस देने या वितरित करने का अधिकार नहीं है, सिवाय इसके कि इस लाइसेंस में स्पष्ट रूप से प्रावधान किया गया हो। किसी भी प्रतिलिपि, संशोधन, सबलाइसेंस देने या वितरण का अनधिकृत प्रयास स्वचालित रूप से आपके अधिकारों को इस लाइसेंस के तहत समाप्त कर देगा।
    
                3. लाइसेंस का स्वचालित निरसन।
    
                आप इस लाइसेंस के तहत अपने अधिकारों का प्रयोग नहीं कर सकते यदि आप इस लाइसेंस की सभी शर्तों और नियमों का पालन नहीं करते हैं। यदि आप इस लाइसेंस की किसी भी शर्त या नियम का उल्लंघन करते हैं, तो आपके अधिकार स्वचालित रूप से निरस्त हो जाएंगे।
    
                4. जिम्मेदारी से मुक्त।
    
                इस लाइसेंस में स्पष्ट रूप से वर्णित स्थिति को छोड़कर, कार्य "जैसा है" प्रदान किया गया है, बिना किसी प्रकार की वारंटी या शर्तों के, चाहे वह स्पष्ट हो या निहित, जिसमें, लेकिन सीमित नहीं, शीर्षक या गैर-उल्लंघन की वारंटी या शर्तें, या व्यावसायिकता या किसी विशेष उद्देश्य के लिए उपयुक्तता की निहित वारंटी या शर्तें शामिल हैं। आप अपने इच्छित परिणाम प्राप्त करने के लिए कार्य का चयन, स्थापना, उपयोग और कार्य से प्राप्त परिणामों की जिम्मेदारी पूरी तरह से खुद लेते हैं।
    
                5. जिम्मेदारी की सीमा।
    
                किसी भी स्थिति में लाइसेंसकर्ता आपके प्रति किसी भी प्रकार के नुकसान, जिसमें अप्रत्यक्ष, विशेष, आकस्मिक या परिणामी नुकसान शामिल हैं, के लिए कार्य या कार्य के उपयोग या वितरण से संबंधित नहीं होगा।
    
                लाइसेंस पाठ
    
                LIVENCRYPT 1.1 परियोजना के लिए लाइसेंस पाठ कई भाषाओं में उपलब्ध है।
    
                6. इस लाइसेंस का भिन्नता।
    
                फ्री सॉफ्टवेयर फाउंडेशन (FSF) समय-समय पर GNU सार्वजनिक सामान्य लाइसेंस के संशोधन और/या नए संस्करण प्रकाशित कर सकती है। इस प्रकार के संशोधन और/या नए संस्करण इस लाइसेंस के तहत बाद में प्रकाशित कार्यों पर प्रासंगिक रूप से लागू होंगे। फाउंडेशन कुछ FSF कार्यक्रमों के लिए अतिरिक्त दिशानिर्देश भी प्रकाशित कर सकती है। इस प्रकार के अतिरिक्त दिशानिर्देश, यदि कोई हो, तो इस कार्य के उद्देश्यों के लिए GNU सार्वजनिक सामान्य लाइसेंस का हिस्सा माना जाएगा।
    
                अंतिम नोट
    
                यह GNU सार्वजनिक सामान्य लाइसेंस है जो कार्य को नियंत्रित करता है। यदि आप इसकी शर्तों और नियमों से सहमत नहीं हैं, तो आपको कार्य की प्रतिलिपि बनाने, संशोधित करने, सबलाइसेंस देने या वितरित करने की अनुमति नहीं है, सिवाय इसके कि इस लाइसेंस में स्पष्ट रूप से प्रावधान किया गया हो। कार्य या इसके व्युत्पन्न की वितरण इस शर्तों की स्वीकृति को इंगित करता है।
    
                """,                            
                "Français": """
        Licence Publique Générale GNU
    
                Version 3, 29 juin 2007
    
                Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
                Tous droits réservés.
    
                Préambule
    
                La Licence Publique Générale GNU est une licence libre, conçue pour garantir la liberté de partager et de modifier les logiciels. Cette licence permet aux utilisateurs la liberté d'utiliser, d'étudier, de partager (copier) et de modifier les logiciels.
    
                Termes et Conditions pour la Copie, la Distribution et la Modification
    
                0. Définitions.
    
                "Ce Licenciant" désigne la personne ou l'entité qui distribue initialement l'œuvre sous cette licence.
    
                "Vous" désigne toute personne qui exerce des droits en vertu de cette licence, que vous ayez reçu ou non l'œuvre directement du licenciant.
    
                "Œuvre" désigne le matériel protégé par le droit d'auteur qui est soumis à cette licence.
    
                "Œuvre Dérivée" désigne toute œuvre protégée par le droit d'auteur, y compris l'œuvre et ses modifications, préparée sous cette licence.
    
                "Texte de la Licence" désigne le texte énoncé dans cette licence.
    
                "Application" désigne toute œuvre dans laquelle l'œuvre ou toute œuvre dérivée de celle-ci a été transformée de telle manière que l'œuvre ou l'œuvre dérivée ne contienne qu'une portion représentative de celle-ci.
    
                "Code Objet Exécutable" désigne le code objet exécutable généré à partir de l'œuvre.
    
                1. Concession de Licence.
    
                Sous réserve des termes et conditions de cette licence, chaque licenciant vous accorde une licence non exclusive, mondiale et perpétuelle pour copier, modifier, exécuter et distribuer l'œuvre, ainsi que pour créer et distribuer des œuvres dérivées de celle-ci, à condition que vous respectiez ce qui suit :
    
                A. La source de l'œuvre doit être accompagnée d'une copie de cette licence. Si l'œuvre et les œuvres dérivées sont distribuées sous forme de code objet exécutable, le texte de cette licence doit être inclus sous une forme facilement lisible dans la documentation associée à la distribution, en utilisant au moins des caractères de taille de police normale.
    
                B. Les modifications introduites par vous doivent être significatives et, dans l'ensemble, représenter un changement substantiel de l'œuvre.
    
                C. Les œuvres dérivées doivent être sous les termes de cette licence.
    
                D. Si l'œuvre comprend un avis de droit d'auteur et/ou d'autres avis légaux se référant à la licence, vous devez conserver ces avis sur toutes les copies que vous faites de l'œuvre ou des œuvres dérivées.
    
                E. Vous ne pouvez pas imposer de termes supplémentaires, ni appliquer de mesure technologique qui restreindrait légalement les autres à exercer les libertés accordées par cette licence.
    
                2. Conditions supplémentaires.
    
                Vous n'êtes pas autorisé à copier, modifier, sous-licencier ou distribuer l'œuvre, sauf expressément prévu par cette licence. Toute tentative de copie, modification, sous-licenciement ou distribution non autorisée invalidera automatiquement votre droit à exercer les droits en vertu de cette licence.
    
                3. Révocation automatique de la Licence.
    
                Vous ne pouvez pas exercer vos droits en vertu de cette licence si vous ne respectez pas toutes les conditions et termes de cette licence. Si une condition ou un terme de cette licence est violé, vos droits seront automatiquement révoqués.
    
                4. Déni de Garantie.
    
                SAUF INDICATION EXPRESSE DANS CETTE LICENCE, L'ŒUVRE EST FOURNIE "EN L'ÉTAT", SANS GARANTIE OU CONDITION D'AUCUNE SORTE, EXPRESSE OU IMPLICITE, Y COMPRIS, MAIS SANS S'Y LIMITER, LES GARANTIES OU CONDITIONS DE TITRE OU DE NON-VIOLATION, OU LES GARANTIES OU CONDITIONS IMPLICITES DE QUALITÉ MARCHANDE OU D'ADÉQUATION À UN USAGE PARTICULIER. VOUS ASSUMEZ LA RESPONSABILITÉ EXCLUSIVE DU CHOIX DE L'ŒUVRE POUR ATTEINDRE LES RÉSULTATS DÉSIRÉS ET DE L'INSTALLATION, DE L'UTILISATION ET DES RÉSULTATS OBTENUS À PARTIR DE L'ŒUVRE.
    
                5. Limitation de Responsabilité.
    
                EN AUCUN CAS LE LICENCIANT NE SERA RESPONSABLE ENVERS VOUS POUR DES DOMMAGES, Y COMPRIS TOUT TYPE DE DOMMAGES INDIRECTS, SPÉCIAUX, ACCESSOIRES OU CONSÉCUTIFS ASSOCIÉS À L'ŒUVRE OU À L'UTILISATION OU LA DISTRIBUTION DE L'ŒUVRE.
    
                Le Texte de la Licence
    
                Le Texte de la Licence pour le projet LIVENCRYPT 1.1 est disponible en plusieurs langues.
    
                6. Variation de cette Licence.
    
                La Free Software Foundation (FSF) peut publier de temps en temps des révisions et/ou de nouvelles versions de la Licence Publique Générale GNU. Ces révisions et/ou nouvelles versions s'appliqueront de manière prospective aux œuvres publiées ultérieurement sous cette licence. La Fondation peut également publier des orientations supplémentaires pour certains programmes de la FSF. Ces orientations supplémentaires, le cas échéant, seront considérées comme faisant partie de la Licence Publique Générale GNU à des fins de cette œuvre.
    
                Note Finale
    
                C'est la Licence Publique Générale GNU qui régit l'œuvre. Si vous n'êtes pas d'accord avec ses termes et conditions, vous n'êtes pas autorisé à copier, modifier, sous-licencier ou distribuer l'œuvre sauf expressément prévu par cette licence. La distribution de l'œuvre ou de ses dérivés implique l'acceptation de ces conditions.
    
                """,
                "عربي": """
        رخصة جنو العمومية العامة
    
                الإصدار 3، 29 يونيو 2007
    
                حقوق الطبع والنشر (C) 2007 مؤسسة البرمجيات الحرة، إنك. <https://fsf.org/>
                جميع الحقوق محفوظة.
    
                المقدمة
    
                رخصة جنو العمومية العامة هي رخصة حرة، مصممة لضمان حرية مشاركة وتعديل البرمجيات. هذه الرخصة تمنح المستخدمين الحرية لاستخدام ودراسة ومشاركة (نسخ) وتعديل البرمجيات.
    
                الشروط والأحكام للنسخ والتوزيع والتعديل
    
                0. التعاريف.
    
                "المرخص" يشير إلى الشخص أو الكيان الذي يوزع العمل في الأصل بموجب هذه الرخصة.
    
                "أنت" يشير إلى أي شخص يمارس حقوقًا بموجب هذه الرخصة، سواء تلقيت العمل مباشرة من المرخص أم لا.
    
                "العمل" يشير إلى المواد المحمية بحقوق الطبع والنشر والتي تخضع لهذه الرخصة.
    
                "العمل المشتق" يشير إلى أي عمل محمي بحقوق الطبع والنشر، بما في ذلك العمل والتعديلات عليه، المُعد بموجب هذه الرخصة.
    
                "نص الرخصة" يشير إلى النص المبين في هذه الرخصة.
    
                "التطبيق" يشير إلى أي عمل تم فيه تحويل العمل أو أي عمل مشتق منه بحيث يحتوي العمل أو العمل المشتق فقط على جزء تمثيلي منه.
    
                "كود الشيء التنفيذي" يشير إلى كود الشيء التنفيذي الذي تم إنشاؤه من العمل.
    
                1. منح الرخصة.
    
                بموجب الشروط والأحكام لهذه الرخصة، يمنحك كل مرخص رخصة غير حصرية وعالمية ودائمة لنسخ وتعديل وتنفيذ وتوزيع العمل، وكذلك لإنشاء وتوزيع أعمال مشتقة منه، بشرط أن تلتزم بما يلي:
    
                أ. يجب أن تكون مصدر العمل مرفقًا بنسخة من هذه الرخصة. إذا تم توزيع العمل والأعمال المشتقة منه في شكل كود الشيء التنفيذي، يجب تضمين نص هذه الرخصة في شكل قابل للقراءة بسهولة في الوثائق المرتبطة بالتوزيع، باستخدام أحرف بحجم الخط العادي على الأقل.
    
                ب. يجب أن تكون التعديلات التي أدخلتها جوهرية وتمثل مجتمعة تغييرًا جوهريًا في العمل.
    
                ج. يجب أن تكون الأعمال المشتقة بموجب شروط هذه الرخصة.
    
                د. إذا كان العمل يتضمن إشعارًا بحقوق الطبع والنشر و/أو إشعارات قانونية أخرى تتعلق بالرخصة، يجب عليك الاحتفاظ بهذه الإشعارات في جميع النسخ التي تقوم بها من العمل أو الأعمال المشتقة.
    
                هـ. لا يمكنك فرض شروط إضافية، ولا تطبيق أي تدبير تكنولوجي يقيد قانونًا الآخرين من ممارسة الحريات الممنوحة بموجب هذه الرخصة.
    
                2. الشروط الإضافية.
    
                لا يُسمح لك بنسخ أو تعديل أو ترخيص فرعي أو توزيع العمل، إلا كما هو منصوص عليه صراحةً في هذه الرخصة. أي محاولة للنسخ أو التعديل أو الترخيص الفرعي أو التوزيع غير المصرح بها ستبطل تلقائيًا حقك في ممارسة الحقوق بموجب هذه الرخصة.
    
                3. الإلغاء التلقائي للرخصة.
    
                لا يمكنك ممارسة حقوقك بموجب هذه الرخصة إذا لم تلتزم بجميع شروط وأحكام هذه الرخصة. إذا تم انتهاك أي شرط أو حكم من هذه الرخصة، فسيتم إلغاء حقوقك تلقائيًا.
    
                4. إخلاء المسؤولية.
    
                باستثناء ما هو منصوص عليه صراحة في هذه الرخصة، يتم تقديم العمل "كما هو"، دون أي ضمانات أو شروط من أي نوع، سواء كانت صريحة أو ضمنية، بما في ذلك، على سبيل المثال لا الحصر، الضمانات أو الشروط المتعلقة بالملكية أو عدم الانتهاك، أو الضمانات أو الشروط الضمنية للقابلية للتسويق أو الملاءمة لغرض معين. تتحمل وحدك المسؤولية عن اختيار العمل لتحقيق النتائج المرجوة وعن التثبيت والاستخدام والنتائج المتحققة من العمل.
    
                5. تحديد المسؤولية.
    
                في أي حال من الأحوال، لن يكون المرخص مسؤولاً أمامك عن أي أضرار، بما في ذلك أي نوع من الأضرار غير المباشرة أو الخاصة أو العرضية أو التبعية المرتبطة بالعمل أو باستخدام أو توزيع العمل.
    
                نص الرخصة
    
                نص الرخصة لمشروع LIVENCRYPT 1.1 متاح بعدة لغات.
    
                6. تعديل هذه الرخصة.
    
                يمكن لمؤسسة البرمجيات الحرة (FSF) أن تصدر من وقت لآخر مراجعات و/أو إصدارات جديدة من رخصة جنو العمومية العامة. ستطبق هذه المراجعات و/أو الإصدارات الجديدة بشكل مستقبلي على الأعمال المنشورة لاحقًا بموجب هذه الرخصة. يمكن للمؤسسة أيضًا نشر إرشادات إضافية لبرامج معينة من FSF. ستعتبر هذه الإرشادات الإضافية، إن وجدت، جزءًا من رخصة جنو العمومية العامة لأغراض هذا العمل.
    
                الملاحظة النهائية
    
                هذه هي رخصة جنو العمومية العامة التي تحكم العمل. إذا كنت لا توافق على شروطها وأحكامها، فلا يُسمح لك بنسخ أو تعديل أو ترخيص فرعي أو توزيع العمل إلا كما هو منصوص عليه صراحةً في هذه الرخصة. إن توزيع العمل أو الأعمال المشتقة منه ينطوي على قبول هذه الشروط.
    
                """,
                "বাংলা": """
        জিএনইউ পাবলিক জেনারেল লাইসেন্স
        
                সংস্করণ ৩, ২৯ জুন ২০০৭
                
                কপিরাইট (সি) ২০০৭ ফ্রি সফটওয়্যার ফাউন্ডেশন, ইনক। <https://fsf.org/>
                সর্বস্বত্ব সংরক্ষিত।
                
                প্রস্তাবনা
                
                জিএনইউ পাবলিক জেনারেল লাইসেন্স একটি মুক্ত লাইসেন্স, যা সফটওয়্যার শেয়ার এবং পরিবর্তন করার স্বাধীনতা নিশ্চিত করার জন্য ডিজাইন করা হয়েছে। এই লাইসেন্স ব্যবহারকারীদের সফটওয়্যার ব্যবহার, অধ্যয়ন, শেয়ার (কপি) এবং পরিবর্তন করার স্বাধীনতা দেয়।
                
                কপি, বিতরণ এবং পরিবর্তনের জন্য শর্তাবলী
                
                ০. সংজ্ঞা।
                
                "এই লাইসেন্সদাতা" বলতে সেই ব্যক্তি বা সত্তাকে বোঝায় যে মূলত এই লাইসেন্সের অধীনে কাজটি বিতরণ করে।
                
                "আপনি" বলতে যেকোনো ব্যক্তি বোঝায় যে এই লাইসেন্সের অধীনে অধিকার প্রয়োগ করে, তা লাইসেন্সদাতার কাছ থেকে সরাসরি কাজটি পেয়েছে কি না।
                
                "কাজ" বলতে কপিরাইট সুরক্ষিত উপাদান বোঝায় যা এই লাইসেন্সের অধীনে থাকে।
                
                "উপজাত কাজ" বলতে কপিরাইট সুরক্ষিত যেকোনো কাজ বোঝায়, যা এই লাইসেন্সের অধীনে প্রস্তুত করা হয়েছে।
                
                "লাইসেন্স টেক্সট" বলতে এই লাইসেন্সের মধ্যে উল্লেখিত পাঠ্য বোঝায়।
                
                "অ্যাপ্লিকেশন" বলতে এমন যেকোনো কাজ বোঝায় যেখানে কাজটি বা এই লাইসেন্সের অধীনে তৈরী উপজাত কাজটি এমনভাবে রূপান্তরিত হয়েছে যে কাজটি বা উপজাত কাজটি শুধুমাত্র একটি প্রতিনিধিত্বমূলক অংশ ধারণ করে।
                
                "অবজেক্ট এক্সিকিউটেবল কোড" বলতে কাজ থেকে তৈরি করা অবজেক্ট এক্সিকিউটেবল কোড বোঝায়।
                
                ১. লাইসেন্স প্রদান।
                
                এই লাইসেন্সের শর্তাবলী অনুযায়ী, প্রতিটি লাইসেন্সদাতা আপনাকে একটি অ-বিশেষ, বিশ্বব্যাপী এবং স্থায়ী লাইসেন্স প্রদান করে কাজটি কপি, পরিবর্তন, সম্পাদন এবং বিতরণ করতে, এবং এর উপজাত কাজ তৈরী এবং বিতরণ করতে, যদি আপনি নিম্নলিখিত শর্তগুলি পূরণ করেন:
                
                ক. কাজের উৎসটি এই লাইসেন্সের একটি কপির সাথে সরবরাহ করতে হবে। যদি কাজ এবং এর উপজাত কাজগুলি অবজেক্ট এক্সিকিউটেবল কোড ফরম্যাটে বিতরণ করা হয়, তবে এই লাইসেন্সের পাঠ্যটি বিতরণ সম্পর্কিত ডকুমেন্টেশনে সহজে পড়ার মতো আকারে অন্তর্ভুক্ত করতে হবে, সাধারণ ফন্ট সাইজ ব্যবহার করে।
                
                খ. আপনার দ্বারা প্রবর্তিত পরিবর্তনগুলি গুরুত্বপূর্ণ হতে হবে এবং সমষ্টিগতভাবে কাজের একটি উল্লেখযোগ্য পরিবর্তনকে প্রতিনিধিত্ব করতে হবে।
                
                গ. উপজাত কাজগুলি এই লাইসেন্সের শর্তাবলীর অধীনে থাকতে হবে।
                
                ঘ. যদি কাজটি কপিরাইট বিজ্ঞপ্তি এবং/অথবা অন্যান্য আইনি বিজ্ঞপ্তি অন্তর্ভুক্ত করে যা লাইসেন্সের সাথে সম্পর্কিত, তবে আপনাকে এই বিজ্ঞপ্তিগুলি রক্ষা করতে হবে আপনি কাজ বা উপজাত কাজগুলির যেকোনো কপিতে।
                
                ঙ. আপনি অতিরিক্ত শর্ত আরোপ করতে পারবেন না, বা কোনো প্রযুক্তিগত ব্যবস্থা প্রয়োগ করতে পারবেন না যা এই লাইসেন্সের অধীনে দেওয়া স্বাধীনতাগুলিকে আইনত সীমাবদ্ধ করে।
                
                ২. অতিরিক্ত শর্তাবলী।
                
                আপনাকে কাজটি কপি, পরিবর্তন, উপ-লাইসেন্স বা বিতরণ করার অনুমতি নেই, যদি না এই লাইসেন্সে স্পষ্টভাবে উল্লেখ করা হয়। যেকোনো অননুমোদিত কপি, পরিবর্তন, উপ-লাইসেন্সিং বা বিতরণ করার চেষ্টা স্বয়ংক্রিয়ভাবে এই লাইসেন্সের অধীনে অধিকার প্রয়োগের আপনার অধিকারকে বাতিল করবে।
                
                ৩. লাইসেন্সের স্বয়ংক্রিয় বাতিল।
                
                আপনি এই লাইসেন্সের সমস্ত শর্তাবলী এবং শর্তগুলি পূরণ না করলে আপনি এই লাইসেন্সের অধীনে আপনার অধিকার প্রয়োগ করতে পারবেন না। যদি এই লাইসেন্সের কোনো শর্ত বা শর্ত লঙ্ঘন হয়, তবে আপনার অধিকার স্বয়ংক্রিয়ভাবে বাতিল হয়ে যাবে।
                
                ৪. দায়বদ্ধতার অব্যাহতি।
                
                এই লাইসেন্সে স্পষ্টভাবে উল্লেখিত না থাকলে, কাজটি "যেমন আছে" সরবরাহ করা হয়, কোনো ধরনের ওয়্যারেন্টি বা শর্ত ছাড়াই, তা স্পষ্ট বা পরোক্ষ হোক, যার মধ্যে, কিন্তু সীমাবদ্ধ নয়, শিরোনামের ওয়্যারেন্টি বা অবমাননার না হওয়ার ওয়্যারেন্টি, বা বাজারযোগ্যতার পরোক্ষ ওয়্যারেন্টি বা নির্দিষ্ট উদ্দেশ্যের জন্য উপযুক্ততার শর্ত অন্তর্ভুক্ত থাকে না। আপনি কাজটি নির্বাচন এবং ইচ্ছাকৃত ফলাফল অর্জনের জন্য ইনস্টলেশন, ব্যবহার এবং প্রাপ্ত ফলাফলের জন্য সম্পূর্ণ দায়িত্ব গ্রহণ করেন।
                
                ৫. দায়বদ্ধতার সীমা।
                
                কোনো পরিস্থিতিতেই লাইসেন্সদাতা আপনার কাছে কাজ বা কাজের ব্যবহার বা বিতরণের সাথে সম্পর্কিত কোনো প্রকার পরোক্ষ, বিশেষ, আকস্মিক বা পরিণতিমূলক ক্ষতির জন্য দায়ী থাকবে না।
                
                লাইসেন্স টেক্সট
                
                প্রকল্প LIVENCRYPT 1.1 এর জন্য লাইসেন্স টেক্সট বিভিন্ন ভাষায় উপলব্ধ।
                
                ৬. এই লাইসেন্সের পরিবর্তন।
                
                ফ্রি সফটওয়্যার ফাউন্ডেশন (FSF) সময়ে সময়ে জিএনইউ পাবলিক জেনারেল লাইসেন্সের পুনর্বিবেচনা এবং/অথবা নতুন সংস্করণ প্রকাশ করতে পারে। এই পুনর্বিবেচনা এবং/অথবা নতুন সংস্করণগুলি ভবিষ্যতে এই লাইসেন্সের অধীনে প্রকাশিত কাজগুলিতে প্রয়োগ করা হবে। ফাউন্ডেশন নির্দিষ্ট FSF প্রোগ্রামগুলির জন্য অতিরিক্ত নির্দেশিকা প্রকাশ করতে পারে। এই অতিরিক্ত নির্দেশিকা, যদি থাকে, এই কাজের উদ্দেশ্যে জিএনইউ পাবলিক জেনারেল লাইসেন্সের অংশ হিসাবে বিবেচিত হবে।
                
                চূড়ান্ত নোট
                
                এই কাজটি পরিচালিত জিএনইউ পাবলিক জেনারেল লাইসেন্স। আপনি যদি এর শর্তাবলী এবং শর্তগুলির সাথে একমত না হন, তাহলে আপনাকে কাজটি কপি, পরিবর্তন, উপ-লাইসেন্স বা বিতরণ করার অনুমতি নেই যদি না এই লাইসেন্সে স্পষ্টভাবে উল্লেখ করা হয়। কাজ বা এর উপজাত কাজগুলি বিতরণ করা এই শর্তগুলির গৃহীত হওয়া বোঝায়।
    
                """,
                "Русский": """
        GNU Общественная Общая Лицензия
        
                Версия 3, 29 июня 2007 года
                
                Авторское право (C) 2007 Фонд Свободного ПО, Инк. <https://fsf.org/>
                Все права защищены.
                
                Преамбула
                
                GNU Общественная Общая Лицензия - это свободная лицензия, созданная для гарантии свободы обмена и изменения программного обеспечения. Эта лицензия предоставляет пользователям свободу использовать, изучать, обмениваться (копировать) и изменять программное обеспечение.
                
                Условия Копирования, Распространения и Изменения
                
                0. Определения.
                
                "Лицензиар" относится к лицу или организации, первоначально распространяющей Работу под данной Лицензией.
                
                "Вы" относится к любому лицу, использующему права под данной Лицензией, независимо от того, получили ли вы Работу непосредственно от Лицензиара.
                
                "Работа" относится к защищенному авторским правом материалу, который подчиняется данной Лицензии.
                
                "Производная Работа" относится к любой работе, защищенной авторским правом, включая Работу и её модификации, подготовленные под данной Лицензией.
                
                "Текст Лицензии" относится к тексту, изложенному в данной Лицензии.
                
                "Приложение" относится к любой работе, в которой Работа или любая производная работа из неё были преобразованы таким образом, что Работа или производная работа содержат только представительную часть.
                
                "Объектный Исполняемый Код" относится к объектному исполняемому коду, созданному из Работы.
                
                1. Предоставление Лицензии.
                
                В соответствии с условиями данной Лицензии, каждый лицензиар предоставляет вам неисключительную, всемирную и бессрочную лицензию на копирование, изменение, выполнение и распространение Работы, а также на создание и распространение производных работ из неё, при условии соблюдения следующих требований:
                
                A. Источник Работы должен сопровождаться копией данной Лицензии. Если Работу и производные работы распространяют в виде объектного исполняемого кода, текст данной Лицензии должен быть включён в документацию, связанную с распространением, в легко читаемой форме, используя как минимум шрифт нормального размера.
                
                B. Внесённые вами изменения должны быть значительными и в совокупности представлять собой существенное изменение Работы.
                
                C. Производные работы должны быть под условиями данной Лицензии.
                
                D. Если Работа содержит уведомление об авторских правах и/или другие юридические уведомления, касающиеся лицензии, вы должны сохранить эти уведомления на всех копиях Работы или производных работ.
                
                E. Вы не можете налагать дополнительные условия или применять какие-либо технологические меры, которые юридически ограничивают других в использовании свобод, предоставленных данной Лицензией.
                
                2. Дополнительные условия.
                
                Вам не разрешается копировать, изменять, предоставлять сублицензии или распространять Работу, за исключением случаев, прямо предусмотренных данной Лицензией. Любая попытка несанкционированного копирования, изменения, предоставления сублицензий или распространения автоматически аннулирует ваше право на использование прав по данной Лицензии.
                
                3. Автоматическое аннулирование Лицензии.
                
                Вы не можете использовать свои права по данной Лицензии, если не выполняете все её условия. Если какое-либо условие данной Лицензии нарушено, ваши права автоматически аннулируются.
                
                4. Отказ от ответственности.
                
                КРОМЕ ЯВНО УСТАНОВЛЕННОГО В ДАННОЙ ЛИЦЕНЗИИ, РАБОТА ПРЕДОСТАВЛЯЕТСЯ "КАК ЕСТЬ", БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ ИЛИ УСЛОВИЙ, ЯВНЫХ ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ, ГАРАНТИИ ИЛИ УСЛОВИЯ ПРАВА СОБСТВЕННОСТИ ИЛИ НЕНАРУШЕНИЯ ПРАВ, ИЛИ ПОДРАЗУМЕВАЕМЫЕ ГАРАНТИИ ИЛИ УСЛОВИЯ КОММЕРЧЕСКОЙ ЦЕННОСТИ ИЛИ ПРИГОДНОСТИ ДЛЯ КОНКРЕТНОЙ ЦЕЛИ. ВЫ НЕСЕТЕ ПОЛНУЮ ОТВЕТСТВЕННОСТЬ ЗА ВЫБОР РАБОТЫ ДЛЯ ДОСТИЖЕНИЯ ЖЕЛАЕМЫХ РЕЗУЛЬТАТОВ, УСТАНОВКУ, ИСПОЛЬЗОВАНИЕ И РЕЗУЛЬТАТЫ, ПОЛУЧЕННЫЕ ОТ РАБОТЫ.
                
                5. Ограничение ответственности.
                
                НИ В КАКОМ СЛУЧАЕ ЛИЦЕНЗИАР НЕ НЕСЁТ ОТВЕТСТВЕННОСТИ ПЕРЕД ВАМИ ЗА УЩЕРБ, ВКЛЮЧАЯ ЛЮБЫЕ КОСВЕННЫЕ, ОСОБЫЕ, СЛУЧАЙНЫЕ ИЛИ ПОСЛЕДУЮЩИЕ УЩЕРБЫ, СВЯЗАННЫЕ С РАБОТОЙ ИЛИ С ИСПОЛЬЗОВАНИЕМ ИЛИ РАСПРОСТРАНЕНИЕМ РАБОТЫ.
                
                Текст Лицензии
                
                Текст Лицензии для проекта LIVENCRYPT 1.1 доступен на нескольких языках.
                
                6. Изменение данной Лицензии.
                
                Фонд Свободного ПО (FSF) может время от времени публиковать пересмотренные и/или новые версии GNU Общественной Общей Лицензии. Эти пересмотренные и/или новые версии будут применяться к Работе, опубликованной под данной Лицензией в будущем. Фонд также может публиковать дополнительные руководства для определённых программ FSF. Эти дополнительные руководства, если они существуют, будут считаться частью GNU Общественной Общей Лицензии для данной Работы.
                
                Заключительное Примечание
                
                Это GNU Общественная Общая Лицензия, регулирующая Работу. Если вы не согласны с её условиями, вам не разрешается копировать, изменять, предоставлять сублицензии или распространять Работу, за исключением случаев, прямо предусмотренных данной Лицензией. Распространение Работы или её производных означает принятие этих условий.
    
                """,
                "Português": """
        Licença Pública Geral GNU
        
                Versão 3, 29 de junho de 2007
                
                Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
                Todos os direitos reservados.
                
                Preâmbulo
                
                A Licença Pública Geral GNU é uma licença livre, projetada para garantir a liberdade de compartilhar e modificar software. Esta licença permite aos usuários a liberdade de usar, estudar, compartilhar (copiar) e modificar o software.
                
                Termos e Condições para Cópia, Distribuição e Modificação
                
                0. Definições.
                
                "Este Licenciante" refere-se à pessoa ou entidade que originalmente distribui o Trabalho sob esta Licença.
                
                "Você" refere-se a qualquer pessoa que exerça direitos sob esta Licença, independentemente de ter recebido ou não o Trabalho diretamente do Licenciante.
                
                "Trabalho" refere-se ao material protegido por direitos autorais que está sujeito a esta Licença.
                
                "Obra Derivada" refere-se a qualquer trabalho protegido por direitos autorais, incluindo o Trabalho e suas modificações, preparado sob esta Licença.
                
                "Texto da Licença" refere-se ao texto enunciado nesta Licença.
                
                "Aplicação" refere-se a qualquer trabalho no qual o Trabalho ou qualquer obra derivada deste tenha sido transformada de tal forma que o Trabalho ou a obra derivada contenham apenas uma porção representativa da mesma.
                
                "Código Objeto Executável" refere-se ao Código Objeto executável gerado a partir do Trabalho.
                
                1. Concessão de Licença.
                
                Sujeito aos termos e condições desta Licença, cada licenciante concede a você uma licença não exclusiva, mundial e perpétua para copiar, modificar, executar e distribuir o Trabalho, bem como para criar e distribuir obras derivadas do mesmo, desde que você cumpra o seguinte:
                
                A. A fonte do Trabalho deve ser acompanhada por uma cópia desta Licença. Se o Trabalho e as obras derivadas forem distribuídos em formato de código objeto executável, o texto desta Licença deve ser incluído de forma facilmente legível na documentação associada à distribuição, utilizando pelo menos caracteres de tamanho de fonte normal.
                
                B. As modificações introduzidas por você devem ser significativas e, no conjunto, representar uma mudança substancial no Trabalho.
                
                C. As obras derivadas devem estar sob os termos desta Licença.
                
                D. Se o Trabalho incluir um aviso de direitos autorais e/ou outros avisos legais que se refiram à licença, você deve manter esses avisos em todas as cópias que você fizer do Trabalho ou das obras derivadas.
                
                E. Você não pode impor termos adicionais, nem aplicar qualquer medida tecnológica que restrinja legalmente outros de exercer as liberdades concedidas por esta Licença.
                
                2. Condições adicionais.
                
                Você não está autorizado a copiar, modificar, sublicenciar ou distribuir o Trabalho, exceto conforme expressamente disposto nesta Licença. Qualquer tentativa de cópia, modificação, sublicenciamento ou distribuição não autorizados invalidará automaticamente seu direito de exercer direitos sob esta Licença.
                
                3. Revogação automática da Licença.
                
                Você não pode exercer seus direitos sob esta Licença se não cumprir todos os termos e condições desta Licença. Se qualquer termo ou condição desta Licença for violado, seus direitos serão revogados automaticamente.
                
                4. Isenção de Responsabilidade.
                
                EXCETO O EXPRESSAMENTE ESTABELECIDO NESTA LICENÇA, O TRABALHO É FORNECIDO "COMO ESTÁ", SEM GARANTIAS OU CONDIÇÕES DE QUALQUER TIPO, SEJAM EXPRESSAS OU IMPLÍCITAS, INCLUINDO, MAS NÃO SE LIMITANDO A, GARANTIAS OU CONDIÇÕES DE TÍTULO OU NÃO INFRAÇÃO, OU GARANTIAS OU CONDIÇÕES IMPLÍCITAS DE COMERCIABILIDADE OU ADEQUAÇÃO PARA UM PROPÓSITO PARTICULAR. VOCÊ ASSUME A RESPONSABILIDADE EXCLUSIVA PELA SELEÇÃO DO TRABALHO PARA ATINGIR SEUS RESULTADOS DESEJADOS E PELA INSTALAÇÃO, USO E RESULTADOS OBTIDOS DO TRABALHO.
                
                5. Limitação de Responsabilidade.
                
                EM NENHUM CASO O LICENCIANTE SERÁ RESPONSÁVEL PERANTE VOCÊ POR DANOS, INCLUINDO QUAISQUER DANOS INDIRETOS, ESPECIAIS, INCIDENTAIS OU CONSEQUENTES ASSOCIADOS AO TRABALHO OU AO USO OU DISTRIBUIÇÃO DO TRABALHO.
                
                Texto da Licença
                
                O Texto da Licença para o projeto LIVENCRYPT 1.1 está disponível em vários idiomas.
                
                6. Alteração desta Licença.
                
                A Free Software Foundation (FSF) pode publicar revisões e/ou novas versões da Licença Pública Geral GNU de tempos em tempos. Essas revisões e/ou novas versões se aplicarão prospectivamente ao Trabalho publicado posteriormente sob esta Licença. A Fundação também pode publicar orientações adicionais para determinados programas da FSF. Essas orientações adicionais, se houver, serão consideradas parte da Licença Pública Geral GNU para os fins deste Trabalho.
                
                Nota Final
                
                Esta é a Licença Pública Geral GNU que governa o Trabalho. Se você não concorda com seus termos e condições, não tem permissão para copiar, modificar, sublicenciar ou distribuir o Trabalho, exceto conforme expressamente disposto nesta Licença. A distribuição do Trabalho ou de suas derivadas implica a aceitação destas condições.
    
                """,
                "Deutsch": """
        GNU General Public License
        
                Version 3, 29. Juni 2007
                
                Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
                Alle Rechte vorbehalten.
                
                Präambel
                
                Die GNU General Public License ist eine freie Lizenz, die entwickelt wurde, um die Freiheit zu gewährleisten, Software zu teilen und zu modifizieren. Diese Lizenz erlaubt den Nutzern die Freiheit, die Software zu verwenden, zu studieren, zu teilen (zu kopieren) und zu modifizieren.
                
                Begriffe und Bedingungen für das Kopieren, Verteilen und Modifizieren
                
                0. Definitionen.
                
                "Dieser Lizenzgeber" bezieht sich auf die Person oder Entität, die das Werk ursprünglich unter dieser Lizenz verbreitet.
                
                "Sie" bezieht sich auf jede Person, die Rechte unter dieser Lizenz ausübt, unabhängig davon, ob sie das Werk direkt vom Lizenzgeber erhalten hat oder nicht.
                
                "Werk" bezieht sich auf das urheberrechtlich geschützte Material, das dieser Lizenz unterliegt.
                
                "Abgeleitetes Werk" bezieht sich auf jedes urheberrechtlich geschützte Werk, einschließlich des Werks und seiner Modifikationen, das unter dieser Lizenz erstellt wurde.
                
                "Lizenztext" bezieht sich auf den in dieser Lizenz angegebenen Text.
                
                "Anwendung" bezieht sich auf jedes Werk, in dem das Werk oder ein abgeleitetes Werk so umgestaltet wurde, dass das Werk oder das abgeleitete Werk nur einen repräsentativen Teil davon enthält.
                
                "Ausführbarer Objektcode" bezieht sich auf den ausführbaren Objektcode, der aus dem Werk erzeugt wurde.
                
                1. Lizenzgewährung.
                
                Vorbehaltlich der Bedingungen dieser Lizenz gewährt Ihnen jeder Lizenzgeber eine nicht exklusive, weltweite und unbefristete Lizenz, das Werk zu kopieren, zu modifizieren, aufzuführen und zu verteilen sowie abgeleitete Werke davon zu erstellen und zu verteilen, sofern Sie die folgenden Bedingungen erfüllen:
                
                A. Die Quelle des Werks muss von einer Kopie dieser Lizenz begleitet werden. Wenn das Werk und die abgeleiteten Werke im Format des ausführbaren Objektcodes verteilt werden, muss der Text dieser Lizenz in einer leicht lesbaren Form in der Dokumentation zur Verteilung enthalten sein, unter Verwendung von mindestens normal großen Schriftzeichen.
                
                B. Die von Ihnen eingeführten Modifikationen müssen signifikant sein und insgesamt eine wesentliche Änderung des Werks darstellen.
                
                C. Die abgeleiteten Werke müssen unter den Bedingungen dieser Lizenz stehen.
                
                D. Wenn das Werk einen Hinweis auf Urheberrechte und/oder andere rechtliche Hinweise enthält, die sich auf die Lizenz beziehen, müssen Sie diese Hinweise in allen Kopien, die Sie vom Werk oder den abgeleiteten Werken machen, beibehalten.
                
                E. Sie dürfen keine zusätzlichen Bedingungen auferlegen oder technische Maßnahmen anwenden, die andere rechtlich daran hindern, die durch diese Lizenz gewährten Freiheiten auszuüben.
                
                2. Zusätzliche Bedingungen.
                
                Sie sind nicht berechtigt, das Werk zu kopieren, zu modifizieren, unterzulizenzieren oder zu verteilen, außer wie in dieser Lizenz ausdrücklich vorgesehen. Jeder Versuch, das Werk unautorisiert zu kopieren, zu modifizieren, unterzulizenzieren oder zu verteilen, wird automatisch Ihre Rechte zur Ausübung von Rechten unter dieser Lizenz ungültig machen.
                
                3. Automatische Lizenzauflösung.
                
                Sie können Ihre Rechte unter dieser Lizenz nicht ausüben, wenn Sie nicht alle Bedingungen dieser Lizenz einhalten. Wenn eine Bedingung dieser Lizenz verletzt wird, werden Ihre Rechte automatisch aufgehoben.
                
                4. Haftungsausschluss.
                
                AUSSER WIE AUSDRÜCKLICH IN DIESER LIZENZ ANGEGEBEN, WIRD DAS WERK "WIE BESEHEN" BEREITGESTELLT, OHNE JEGLICHE GARANTIEN ODER BEDINGUNGEN, WEDER AUSDRÜCKLICH NOCH IMPLIZIT, EINSCHLIESSLICH, ABER NICHT BESCHRÄNKT AUF GARANTIEN ODER BEDINGUNGEN DES TITELS ODER DER NICHTVERLETZUNG, ODER IMPLIZITE GARANTIEN ODER BEDINGUNGEN DER MARKTGÄNGIGKEIT ODER EIGNUNG FÜR EINEN BESTIMMTEN ZWECK. SIE ÜBERNEHMEN DIE ALLEINIGE VERANTWORTUNG FÜR DIE AUSWAHL DES WERKS, UM IHRE GEWÜNSCHTEN ERGEBNISSE ZU ERZIELEN, UND FÜR DIE INSTALLATION, DIE NUTZUNG UND DIE ERGEBNISSE, DIE AUS DEM WERK ERZIELT WERDEN.
                
                5. Haftungsbeschränkung.
                
                IN KEINEM FALL HAFTET DER LIZENZGEBER IHNEN GEGENÜBER FÜR SCHÄDEN, EINSCHLIESSLICH INDIREKTER, SPEZIELLER, ZUFÄLLIGER ODER FOLGESCHÄDEN IM ZUSAMMENHANG MIT DEM WERK ODER DER NUTZUNG ODER VERTEILUNG DES WERKS.
                
                Lizenztext
                
                Der Lizenztext für das Projekt LIVENCRYPT 1.1 ist in mehreren Sprachen verfügbar.
                
                6. Änderung dieser Lizenz.
                
                Die Free Software Foundation (FSF) kann von Zeit zu Zeit Überarbeitungen und/oder neue Versionen der GNU General Public License veröffentlichen. Diese Überarbeitungen und/oder neuen Versionen gelten für das Werk, das nachfolgend unter dieser Lizenz veröffentlicht wird. Die Stiftung kann auch zusätzliche Richtlinien für bestimmte Programme der FSF veröffentlichen. Diese zusätzlichen Richtlinien, falls vorhanden, werden für die Zwecke dieses Werks als Teil der GNU General Public License betrachtet.
                
                Schlussbemerkung
                
                Dies ist die GNU General Public License, die das Werk regelt. Wenn Sie den Bedingungen nicht zustimmen, haben Sie keine Erlaubnis, das Werk zu kopieren, zu modifizieren, unterzulizenzieren oder zu verteilen, außer wie in dieser Lizenz ausdrücklich vorgesehen. Die Verteilung des Werks oder seiner abgeleiteten Werke impliziert die Annahme dieser Bedingungen.
    
                """,
                "日本語": """
        GNU一般公衆利用許諾契約書
        
                バージョン3、2007年6月29日
                
                著作権 (C) 2007 フリーソフトウェア財団, Inc. <https://fsf.org/>
                全著作権所有。
                
                前文
                
                GNU一般公衆利用許諾契約書は、ソフトウェアを共有し、変更する自由を保障するために設計された自由なライセンスです。このライセンスは、ユーザーにソフトウェアを使用し、研究し、共有（コピーし）、変更する自由を許可します。
                
                複製、配布および変更のための条項と条件
                
                0. 定義。
                
                「本ライセンサー」とは、このライセンスの下で最初に作品を配布する人物または団体を指します。
                
                「あなた」とは、このライセンスの下で権利を行使する人物を指し、ライセンサーから直接作品を受け取ったかどうかは問いません。
                
                「作品」とは、このライセンスの対象となる著作権で保護された素材を指します。
                
                「派生作品」とは、このライセンスの下で作成された作品およびその変更を含む、著作権で保護された任意の作品を指します。
                
                「ライセンステキスト」とは、このライセンスで述べられているテキストを指します。
                
                「アプリケーション」とは、作品またはその派生作品が変形され、その代表的な部分のみを含むように変形された任意の作品を指します。
                
                「実行可能なオブジェクトコード」とは、作品から生成された実行可能なオブジェクトコードを指します。
                
                1. ライセンスの付与。
                
                このライセンスの条項と条件に従うことを条件に、各ライセンサーはあなたに対し、作品をコピー、変更、実行および配布し、それから派生した作品を作成および配布するための非独占的、世界的、永続的なライセンスを付与します。以下の条件に従うことを条件とします：
                
                A. 作品のソースには、このライセンスのコピーを添付する必要があります。作品および派生作品が実行可能なオブジェクトコード形式で配布される場合、このライセンスのテキストは、配布に関連する文書内に、少なくとも通常のフォントサイズの文字を使用して読みやすい形式で含まれる必要があります。
                
                B. あなたが導入する変更は重要であり、全体として作品に対する実質的な変更を表している必要があります。
                
                C. 派生作品は、このライセンスの条項の下でなければなりません。
                
                D. 作品が著作権表示および/またはライセンスに言及する他の法的通知を含む場合、あなたが作品または派生作品のコピーを作成するすべてのコピーにこれらの通知を保持する必要があります。
                
                E. あなたは追加の条件を課すことはできず、このライセンスによって付与された自由を他者が合法的に行使することを制限する技術的手段を適用することはできません。
                
                2. 追加の条件。
                
                あなたは、このライセンスで明示的に規定されている場合を除き、作品をコピー、変更、サブライセンス、または配布する権限を持っていません。無許可のコピー、変更、サブライセンス、または配布の試みは、自動的にこのライセンスの下で権利を行使する権利を無効にします。
                
                3. ライセンスの自動解除。
                
                あなたがこのライセンスのすべての条項と条件を遵守しない限り、このライセンスの下での権利を行使することはできません。このライセンスのいずれかの条項または条件に違反した場合、あなたの権利は自動的に解除されます。
                
                4. 免責条項。
                
                このライセンスで明示的に定められている場合を除き、作品は「現状のまま」提供され、明示的または黙示的な保証や条件、特にタイトルまたは非侵害の保証や条件、商品性または特定の目的への適合性の黙示的な保証や条件を含む、いかなる種類の保証や条件も含みません。あなたは、望ましい結果を達成するために作品を選択し、インストールし、使用し、作品から得られる結果について全責任を負います。
                
                5. 責任の制限。
                
                いかなる場合も、ライセンサーは、作品またはその使用または配布に関連する間接的、特別、偶発的、または結果的な損害に対して、あなたに対して責任を負いません。
                
                ライセンステキスト
                
                プロジェクトLIVENCRYPT 1.1のライセンステキストは、複数の言語で利用可能です。
                
                6. このライセンスの変更。
                
                フリーソフトウェア財団（FSF）は、時折、GNU一般公衆利用許諾契約書の改訂版および/または新しいバージョンを発行することがあります。これらの改訂版および/または新しいバージョンは、このライセンスの下で後で発行された作品に対して適用されます。財団はまた、特定のFSFプログラムに関する追加のガイダンスを発行することがあります。これらの追加のガイダンスがある場合、それらはこの作品のためのGNU一般公衆利用許諾契約書の一部とみなされます。
    
                """,
                "Türkçe": """
        GNU Genel Kamu Lisansı
        
                Sürüm 3, 29 Haziran 2007
                
                Telif Hakkı (C) 2007 Özgür Yazılım Vakfı, Inc. <https://fsf.org/>
                Tüm hakları saklıdır.
                
                Ön Söz
                
                GNU Genel Kamu Lisansı, yazılımı paylaşma ve değiştirme özgürlüğünü garanti altına almak için tasarlanmış özgür bir lisanstır. Bu lisans, kullanıcılara yazılımı kullanma, inceleme, paylaşma (kopyalama) ve değiştirme özgürlüğü sağlar.
                
                Kopyalama, Dağıtım ve Değiştirme Şartları ve Koşulları
                
                0. Tanımlar.
                
                "Bu Lisans Veren", bu Lisans altında eseri ilk kez dağıtan kişi veya kuruluşu ifade eder.
                
                "Siz", bu Lisans altında hakları kullanan herhangi bir kişiyi ifade eder, eseri doğrudan lisans verenden almış olup olmadığına bakılmaksızın.
                
                "Eser", bu Lisansın konusu olan telif hakkıyla korunan materyali ifade eder.
                
                "Türev Eser", bu Lisans altında hazırlanan eser ve onun değişiklikleri dahil olmak üzere, telif hakkıyla korunan herhangi bir eseri ifade eder.
                
                "Lisans Metni", bu Lisansta belirtilen metni ifade eder.
                
                "Uygulama", eser veya türev eserinin yalnızca temsili bir kısmını içerecek şekilde dönüştürüldüğü herhangi bir eseri ifade eder.
                
                "Çalıştırılabilir Nesne Kodu", eserden üretilen çalıştırılabilir nesne kodunu ifade eder.
                
                1. Lisans Verilmesi.
                
                Bu Lisansın şart ve koşullarına tabi olarak, her bir lisans veren, size eseri kopyalama, değiştirme, icra etme ve dağıtma, ayrıca türev eserler yapma ve dağıtma konusunda münhasır olmayan, dünya çapında ve kalıcı bir lisans verir, şu şartlara uyduğunuz sürece:
                
                A. Eserin kaynağına, bu Lisansın bir kopyası eşlik etmelidir. Eser ve türev eserler çalıştırılabilir nesne kodu formatında dağıtılıyorsa, bu Lisansın metni, dağıtımla ilgili belgelerde, en azından normal yazı tipi boyutundaki karakterler kullanılarak kolayca okunabilir bir şekilde yer almalıdır.
                
                B. Sizin tarafınızdan yapılan değişiklikler önemli olmalı ve bir bütün olarak eserde önemli bir değişikliği temsil etmelidir.
                
                C. Türev eserler, bu Lisansın şartlarına tabi olmalıdır.
                
                D. Eser, telif hakkı bildirimi ve/veya lisansa atıfta bulunan diğer yasal bildirimler içeriyorsa, eser veya türev eserlerin yaptığınız tüm kopyalarında bu bildirimleri korumalısınız.
                
                E. Ek şartlar koyamazsınız veya bu Lisansta verilen özgürlükleri başkalarının yasal olarak kullanmasını kısıtlayacak teknolojik önlemler uygulayamazsınız.
                
                2. Ek Şartlar.
                
                Bu Lisansta açıkça belirtilen haller dışında, eseri kopyalama, değiştirme, alt lisans verme veya dağıtma yetkisine sahip değilsiniz. Yetkisiz kopyalama, değiştirme, alt lisans verme veya dağıtma girişimleri, bu Lisans altında hakları kullanma yetkinizi otomatik olarak geçersiz kılacaktır.
                
                3. Lisansın Otomatik İptali.
                
                Bu Lisanstaki tüm şartlara ve koşullara uymadığınız sürece, bu Lisans altında haklarınızı kullanamazsınız. Bu Lisansın herhangi bir şartı veya koşulu ihlal edilirse, haklarınız otomatik olarak iptal edilir.
                
                4. Sorumluluk Reddi.
                
                BU LİSANSDA AÇIKÇA BELİRTİLEN DURUMLAR HARİÇ OLMAK ÜZERE, ESER "OLDUĞU GİBİ" SAĞLANIR VE AÇIK VEYA ZIMNİ HERHANGİ BİR GARANTİ VEYA KOŞUL İÇERMEZ, BUNLAR SINIRLI OLMAYAN BAŞLIK VEYA İHLAL ETMEME GARANTİLERİ VEYA BELİRLİ BİR AMACA UYGUNLUK VE TİCARİ DEĞERLİLİK ZIMNİ GARANTİLERİ VEYA KOŞULLARINI DA KAPSAR. İSTENEN SONUÇLARI ELDE ETMEK İÇİN ESERİ SEÇME VE KURMA, KULLANMA VE ELDE EDİLEN SONUÇLARDAN TAMAMEN SİZ SORUMLUSUNUZ.
                
                5. Sorumluluğun Sınırlandırılması.
                
                HİÇBİR DURUMDA LİSANS VEREN, ESERİN KULLANIMI VEYA DAĞITIMI İLE İLGİLİ OLARAK SİZE KARŞI HERHANGİ BİR TÜRDEKİ DOLAYLI, ÖZEL, ARIZİ VEYA SONUÇSAL ZARARLARDAN SORUMLU OLMAYACAKTIR.
                
                Lisans Metni
                
                LIVENCRYPT 1.1 projesi için Lisans Metni, birden fazla dilde mevcuttur.
                
                6. Bu Lisansın Değiştirilmesi.
                
                Özgür Yazılım Vakfı (FSF), zaman zaman GNU Genel Kamu Lisansının revizyonlarını ve/veya yeni sürümlerini yayınlayabilir. Bu tür revizyonlar ve/veya yeni sürümler, bu Lisans altında daha sonra yayınlanan eserlere uygulanacaktır. Vakıf ayrıca belirli FSF programları için ek rehberlik yayınlayabilir. Bu ek rehberlikler mevcutsa, bu eser için GNU Genel Kamu Lisansının bir parçası olarak kabul edilecektir.
                
                Son Not
                
                Bu, eseri yöneten GNU Genel Kamu Lisansıdır. Şartlarını ve koşullarını kabul etmiyorsanız, eseri kopyalama, değiştirme, alt lisans verme veya dağıtma izniniz yoktur, bu Lisansta açıkça belirtilen durumlar dışında. Eserin veya türevlerinin dağıtımı, bu şartların kabulünü içerir.
    
                """,
                "한국어": """
        GNU 일반 공중 라이센스
        
                버전 3, 2007년 6월 29일
                
                저작권 (C) 2007 자유 소프트웨어 재단, Inc. <https://fsf.org/>
                모든 권리 보유.
                
                서문
                
                GNU 일반 공중 라이센스는 소프트웨어를 공유하고 수정할 자유를 보장하기 위해 설계된 자유로운 라이센스입니다. 이 라이센스는 사용자가 소프트웨어를 사용하고, 연구하고, 공유(복사)하며, 수정할 자유를 허용합니다.
                
                복사, 배포 및 수정에 대한 조건
                
                0. 정의.
                
                "이 라이센스 제공자"는 이 라이센스 하에 작품을 처음 배포하는 사람 또는 단체를 의미합니다.
                
                "귀하"는 이 라이센스 하에 권리를 행사하는 모든 사람을 의미하며, 라이센스 제공자로부터 직접 작품을 받았는지 여부에 관계없이 포함됩니다.
                
                "작품"은 이 라이센스의 적용을 받는 저작권으로 보호된 자료를 의미합니다.
                
                "파생 작업"은 저작권으로 보호되는 모든 작업을 의미하며, 여기에는 작품과 그 수정 사항이 포함됩니다. 이 라이센스 하에서 준비된 작업을 의미합니다.
                
                "라이센스 텍스트"는 이 라이센스에 명시된 텍스트를 의미합니다.
                
                "응용 프로그램"은 작품 또는 이의 파생 작업이 변형되어 작품 또는 파생 작업이 해당 작업의 대표적인 일부만 포함된 작업을 의미합니다.
                
                "실행 가능한 객체 코드"는 작품에서 생성된 실행 가능한 객체 코드를 의미합니다.
                
                1. 라이센스 부여.
                
                이 라이센스의 조건 및 조항에 따라, 각 라이센스 제공자는 귀하에게 작품을 복사, 수정, 실행 및 배포할 수 있는 비독점적, 전 세계적, 영구적인 라이센스를 부여합니다. 또한, 귀하가 다음 조건을 충족하는 한, 파생 작업을 만들고 배포할 수 있습니다:
                
                A. 작품의 소스는 이 라이센스의 사본과 함께 제공되어야 합니다. 작품과 파생 작업이 실행 가능한 객체 코드 형식으로 배포되는 경우, 이 라이센스의 텍스트는 배포와 관련된 문서에 쉽게 읽을 수 있는 형태로 포함되어야 하며, 최소한 일반 글꼴 크기의 문자로 작성되어야 합니다.
                
                B. 귀하가 수행한 수정은 중요해야 하며, 전체적으로 작품에 실질적인 변경을 의미해야 합니다.
                
                C. 파생 작업은 이 라이센스의 조건에 따라야 합니다.
                
                D. 작품에 저작권 통지 및/또는 라이센스를 참조하는 기타 법적 통지가 포함된 경우, 귀하가 작품 또는 파생 작업의 모든 복사본을 만들 때 이러한 통지를 보존해야 합니다.
                
                E. 추가 조건을 부과하거나 이 라이센스에서 부여된 자유를 다른 사람들이 법적으로 제한하는 기술적 조치를 적용할 수 없습니다.
                
                2. 추가 조건.
                
                이 라이센스에서 명시적으로 허용된 경우를 제외하고는, 작품을 복사, 수정, 서브 라이센스하거나 배포할 권한이 없습니다. 무단 복사, 수정, 서브 라이센스 또는 배포 시도는 자동으로 이 라이센스 하의 권리를 행사할 수 있는 권한을 무효화합니다.
                
                3. 라이센스의 자동 해지.
                
                이 라이센스의 모든 조건 및 조항을 준수하지 않는 경우, 이 라이센스 하에서 권리를 행사할 수 없습니다. 이 라이센스의 조건 또는 조항을 위반하면, 귀하의 권리는 자동으로 해지됩니다.
                
                4. 면책 조항.
                
                이 라이센스에서 명시적으로 규정된 경우를 제외하고, 작품은 "있는 그대로" 제공되며, 명시적이거나 묵시적인 어떠한 보증이나 조건도 제공되지 않습니다. 여기에는 제목이나 비침해 보증, 상업성 또는 특정 목적에 적합성에 대한 묵시적 보증이나 조건이 포함되지만 이에 국한되지 않습니다. 귀하는 원하는 결과를 얻기 위해 작품을 선택하고 설치, 사용 및 결과에 대한 전적인 책임을 집니다.
                
                5. 책임의 제한.
                
                어떤 경우에도 라이센스 제공자는 작품의 사용 또는 배포와 관련하여 귀하에게 간접적, 특별한, 우발적인 또는 결과적인 손해에 대해 책임을 지지 않습니다.
                
                라이센스 텍스트
                
                LIVENCRYPT 1.1 프로젝트에 대한 라이센스 텍스트는 여러 언어로 제공됩니다.
                
                6. 이 라이센스의 변경.
                
                자유 소프트웨어 재단(FSF)은 때때로 GNU 일반 공중 라이센스의 개정판 및/또는 새로운 버전을 게시할 수 있습니다. 이러한 개정판 및/또는 새로운 버전은 이후에 이 라이센스 하에 발표된 작품에 적용됩니다. 재단은 또한 특정 FSF 프로그램에 대한 추가 지침을 게시할 수 있습니다. 이러한 추가 지침이 있을 경우, 이 작품에 대해 GNU 일반 공중 라이센스의 일부로 간주됩니다.
                
                최종 주의 사항
                
                이 GNU 일반 공중 라이센스는 작품을 규율합니다. 이 라이센스의 조건 및 조항에 동의하지 않는 경우, 이 라이센스에서 명시적으로 허용된 경우를 제외하고는 작품을 복사, 수정, 서브 라이센스 또는 배포할 권한이 없습니다. 작품 또는 그 파생 작업의 배포는 이러한 조건의 수락을 의미합니다.
    
            """,
        }
             
    def actualizar_tamano_fuente(self):
        self.configurar_estilos()
        self.actualizar_todas_ventanas()
    
    def cargar_traducciones(self):
        self.medidas_plantilla = {
            "(2, 56)": (2, 56),
            "(4, 28)": (4, 28),
            "(7, 16)": (7, 16),
            "(8, 14)": (8, 14),
            "(14, 8)": (14, 8),
            "(16, 7)": (16, 7),
            "(28, 4)": (28, 4),
            "(3, 56)": (3, 56),
            "(4, 56)": (4, 56),
            "(5, 56)": (5, 56),
            "(7, 56)": (7, 56),
            "(8, 56)": (8, 56),
            "(10, 56)": (10, 56),
            "(11, 56)": (11, 56),
            "(14, 56)": (14, 56),
            }
            
        # Aquí deberías cargar las traducciones desde un archivo o diccionario
        self.traducciones = {
            "Español": {
                "112": '112',
                "(2, 56)": "(2, 56)", "(4, 28)": "(4, 28)", "(7, 16)": "(7, 16)", 
                "(8, 14)": "(8, 14)", "(14, 8)": "(14, 8)", "(16, 7)": "(16, 7)", 
                "(28, 4)": "(28, 4)", "(3, 56)": "(3, 56)", "(4, 56)": "(4, 56)", 
                "(5, 56)": "(5, 56)", "(7, 56)": "(7, 56)", "(8, 56)": "(8, 56)", 
                "(10, 56)": "(10, 56)", "(11, 56)": "(11, 56)", "(14, 56)": "(14, 56)",
                "titulo_cifrar_descifrar": "Cifrar o Descifrar",
                "opcion_cifrar": "Cifrar",
                "opcion_descifrar": "Descifrar",
                "boton_aceptar": "Aceptar",
                "seleccionar_fichero": "Seleccionar archivo",
                "titulo_cifrar_descifrar": "Cifrar o Descifrar",
                "opcion_cifrar": "Cifrar",
                "opcion_descifrar": "Descifrar",
                "boton_aceptar": "Aceptar",
                "cifrado": "cifrado",
                "descifrado": "descifrado",
                "descifrado_guardado": "Archivo descifrado guardado.",
                "bytes": "bytes",
                "total_caracteres_original": "Total caracteres original",
                "total_caracteres_hexadecimal": "Total caracteres hexadecimal",
                "convertido_a_hexadecimal": "Convertido a hexadecimal",
                "archivo_temporal_creado": "Archivo temporal creado",
                "insertar_referencia_titulo": "Insertar Referencia",
                "insertar_referencia_mensaje": "Inserte la referencia (sin espacios):",
                "referencia_encontrada_eliminada": "Referencia encontrada y eliminada. Correcto.",
                "referencia_no_encontrada": "La referencia no ha sido encontrada.",
                "no_procesar_archivo": "No se pudo procesar el archivo",
                "archivo_temporal_eliminado": "Fichero temporal eliminado",              
                "archivo_guardado": "Archivo guardado correctamente",
                "cajas_vacias": "Las cajas no pueden estar vacías",
                "cargar_fichero": "Cargar archivo",
                "cifrado_guardado": "Cifrado guardado en formato hexadecimal",
                "cifrado_realizado": "Cifrado realizado",
                "contenido_guardado": "Contenido guardado",
                "descifrado_guardado_original": "Descifrado guardado en formato original",
                "descifrado_realizado": "Descifrado realizado",
                "error_hex_impar": "El contenido hexadecimal no tiene un número par de caracteres.",
                "exito": "Éxito",
                "extension_mensaje": "Ingrese la extensión del archivo original (por ejemplo, .png, .jpg, .txt):",
                "extension_titulo": "Extensión del archivo",
                "file_encryption": "Encriptar archivos",
                "guardar": "Guardar",
                "hex_invalido": "El contenido hexadecimal no es válido y no se puede convertir a binario.",
                "ingrese_numeros": "Por favor, ingrese solo números en todas las cajas y asegúrese de que ninguna esté vacía.",
                "invalid_hex": "El contenido hexadecimal no tiene un número par de caracteres.",
                "nocontenido": "No hay contenido para procesar",
                "no_cargar_archivo": "No se pudo cargar el archivo",
                "noguardar": "No se puede guardar el archivo.",
                "seleccionar_fichero": "Seleccionar archivo",
                "tamano_archivo": "Tamaño del archivo",
                "temp_file_creado": "Archivo temporal creado",
                "temp_file_deleted": "Ficheros temporal eliminado",
                "total_caracteres": "Total caracteres",         
                "aceptar": "Aceptar",
                "advertencia": "Error insertando caracteres.",
                "advertencia1": "El carácter '{}' ya ha sido utilizado",
                "advertencia2": "Se ha excedido el límite de caracteres. Se eliminarán los caracteres sobrantes.",
                "agregar_todos": "Agregar todos:",
                "ajustes": "Ajustes",
                "aleatoriedad": "Aleatorizar",
                "aplicar": "Aplicar",
                "borrar_caracter": "Borrar último carácter",
                "cambiar_idioma": "Cambiar idioma",
                "cambiar_tamano_letra": "Cambiar tamaño de letra",
                "cancelar": "Cancelar",
                "caracteres": "caracteres",
                "caracteres_idiomas": "Caracteres idiomas",
                "caracteres_restantes": "Caracteres restantes:",
                "caracteres_por_idiomas": "Caracteres por idioma",
                "cifrar": "Cifrar",
                "cifrar_texto": "Cifrar texto",
                "confirmar": "Confirmar",
                "confirmar_eliminar_plantilla": "Confirme la eliminación de la plantilla",
                "consejos": "Consejos",
                "contraseña_requerida": "Se requiere contraseña",
                "crear_plantilla": "Crear plantilla",
                "creditos": "Créditos",
                "descifrar": "Descifrar",
                "descifrar_texto": "Descifrar texto",
                "editar": "Editar",
                "editar_plantilla": "Editar plantilla",
                "editar_plantilla_existente": "Editar plantilla existente",
                "ejecutar": "Ejecutar",
                "eliminar": "Eliminar",
                "error": "Error",
                "error_ingresar_valores": "Por favor, ingresa todos los valores.",
                "error_valores_numeros": "Los valores deben ser números entre 0 y 1000.",
                "excedido_intentos_mensaje": "Has excedido el número máximo de intentos. Se ha ejecutado un sobrecalentamiento del voltaje para que explote su dispositivo...",
                "faq": "Preguntas Frecuentes",
                "formato_invalido": "Formato de plantilla inválido. Asegúrese de que sea una lista de caracteres separados por comas.",
                "gestionar_plantillas": "Gestionar plantillas",
                "guardar_plantilla": "Guardar plantilla",
                "guardada_correctamente": "La plantilla '{}' se ha guardado correctamente",
                "ingresa_contraseña": "Ingresa la contraseña",
                "ingrese_nombre_plantilla": "Ingrese un nombre para la plantilla:",
                "info": "Crea una plantilla",
                "info2": "Selecciona una opción",
                "info3": "Eliminar plantilla",
                "info_funcion_no_implementada": "No has seleccionado una opción: cifrar, descifrar o gestionar plantillas.",
                "intenta_nuevamente": "Error en la contraseña, inténtalo de nuevo",
                "licencia": "Licencia",
                "limpiar": "Limpiar",
                "No_hay_plantillas_nuevas_creadas_para_editar": "No hay plantillas nuevas creadas para editar",
                "No_plantilla_seleccionada_no_existe": "No hay plantilla seleccionada o la plantilla no existe",
                "Nueva_plantilla_creada": "Nueva plantilla creada",
                "nuevo_tamano_letra": "Nuevo tamaño de letra:",
                "numero_invalido": "Por favor, ingrese un número válido",
                "Numeros/signos": "Números/signos",
                "Plantilla_1": "Latino",
                "Plantilla_2": "Euroasiáticos",
                "Plantilla_3": "Árabe, Amharico, Cherokee",
                "Plantilla_4": "Chino",
                "Plantilla_5": "Asiáticos",
                "plantilla_eliminada": "La plantilla '{}' ha sido eliminada",
                "plantilla_en_construccion": "Plantilla en construcción:",
                "plantilla_no_coincide": "La plantilla no coincide",
                "salir": "Salir",
                "Selecciona_la_plantilla_a_editar": "Selecciona la plantilla a editar",
                "seleccionar_plantilla": "Selecciona plantilla:",
                "seleccionar_tamaño": "Selecciona tamaño",
                "seleccione_idiomas": "Seleccione idiomas",
                "Signos": "Signos",
                "solicitar_contraseña": "Ingresa la contraseña",
                "tamano_fuera_rango": "El tamaño debe estar entre 8 y 24",
                "texto": "Texto:",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "Valor 1:",
                "valor_2": "Valor 2:",
                "valor_3": "Valor 3:",
                "valor_4": "Valor 4:",
                "valor_5": "Valor 5:",
                "Aleman": "Alemán",
                "Amharico": "Amhárico",
                "Arabe_clasico": "Árabe clásico",
                "Arabigos": "Arábigos",
                "Armenio": "Armenio",
                "Bengali": "Bengalí",
                "Birmano": "Birmano",
                "Cherokee": "Cherokee",
                "Checo": "Checo",
                "Chino": "Chino",
                "Coreano": "Coreano",
                "Devanagari": "Devanagari",
                "Escandinavo": "Escandinavo",
                "Espanol": "Español",
                "Etiope": "Etíope",
                "Frances": "Francés",
                "Gales": "Galés",
                "Georgiano": "Georgiano",
                "Griego": "Griego",
                "Hindi": "Hindi",
                "Hungaro": "Húngaro",
                "Ingles": "Inglés",
                "Islandes": "Islandés",
                "Japones": "Japonés",
                "Katakana": "katakana",
                "Kannada": "Kannada",
                "Khmer": "Khmer",
                "Leton": "Letón",
                "Lituano": "Lituano",
                "Numeros/especiales": "Números/especiales",
                "Polaco": "Polaco",
                "Portugues": "Portugués",
                "Rumano": "Rumano",
                "Ruso": "Ruso",
                "Thai": "Thai",
                "Tibetano": "Tibetano",
                "Turco": "Turco",
                "Vietnamita": "Vietnamita",
            },
            "English": {
                "112": '112',
                "(2, 56)": "(2, 56)", "(4, 28)": "(4, 28)", "(7, 16)": "(7, 16)", 
                "(8, 14)": "(8, 14)", "(14, 8)": "(14, 8)", "(16, 7)": "(16, 7)", 
                "(28, 4)": "(28, 4)", "(3, 56)": "(3, 56)", "(4, 56)": "(4, 56)", 
                "(5, 56)": "(5, 56)", "(7, 56)": "(7, 56)", "(8, 56)": "(8, 56)", 
                "(10, 56)": "(10, 56)", "(11, 56)": "(11, 56)", "(14, 56)": "(14, 56)",
                "titulo_cifrar_descifrar": "Encrypt or Decrypt",
                "opcion_cifrar": "Encrypt",
                "opcion_descifrar": "Decrypt",
                "boton_aceptar": "Accept",
                "seleccionar_fichero": "Select file",
                "cifrado": "encryption",
                "descifrado": "decryption",
                "descifrado_guardado": "Decrypted file saved.",
                "bytes": "bytes",
                "total_caracteres_original": "Total original characters",
                "total_caracteres_hexadecimal": "Total hexadecimal characters",
                "convertido_a_hexadecimal": "Converted to hexadecimal",
                "archivo_temporal_creado": "Temporary file created",
                "insertar_referencia_titulo": "Insert Reference",
                "insertar_referencia_mensaje": "Insert the reference (without spaces):",
                "referencia_encontrada_eliminada": "Reference found and removed. Success.",
                "referencia_no_encontrada": "Reference not found.",
                "no_procesar_archivo": "Could not process the file",
                "archivo_temporal_eliminado": "Temporary file deleted",
                "archivo_guardado": "File saved successfully",
                "cajas_vacias": "Boxes cannot be empty",
                "cargar_fichero": "Load file",
                "cifrado_guardado": "Encryption saved in hexadecimal format",
                "cifrado_realizado": "Encryption performed",
                "contenido_guardado": "Content saved",
                "descifrado_guardado_original": "Decryption saved in original format",
                "descifrado_realizado": "Decryption performed",
                "error_hex_impar": "The hexadecimal content does not have an even number of characters.",
                "exito": "Success",
                "extension_mensaje": "Enter the extension of the original file (e.g., .png, .jpg, .txt):",
                "extension_titulo": "File extension",
                "file_encryption": "Encrypt files",
                "guardar": "Save",
                "hex_invalido": "The hexadecimal content is invalid and cannot be converted to binary.",
                "ingrese_numeros": "Please enter only numbers in all boxes and ensure none are empty.",
                "invalid_hex": "The hexadecimal content does not have an even number of characters.",
                "nocontenido": "No content to process",
                "no_cargar_archivo": "Could not load the file",
                "noguardar": "Cannot save the file.",
                "seleccionar_fichero": "Select file",
                "tamano_archivo": "File size",
                "temp_file_creado": "Temporary file created",
                "temp_file_deleted": "Temporary file deleted",
                "total_caracteres": "Total characters",
                "aceptar": "Accept",
                "advertencia": "Error inserting characters.",
                "advertencia1": "The character '{}' has already been used",
                "advertencia2": "The character limit has been exceeded. Excess characters will be removed.",
                "agregar_todos": "Add all:",
                "ajustes": "Settings",
                "aleatoriedad": "Randomize",
                "aplicar": "Apply",
                "borrar_caracter": "Delete last character",
                "cambiar_idioma": "Change language",
                "cambiar_tamano_letra": "Change font size",
                "cancelar": "Cancel",
                "caracteres": "characters",
                "caracteres_idiomas": "Language characters",
                "caracteres_restantes": "Remaining characters:",
                "caracteres_por_idiomas": "Characters per language",
                "cifrar": "Encrypt",
                "cifrar_texto": "Encrypt text",
                "confirmar": "Confirm",
                "confirmar_eliminar_plantilla": "Confirm template deletion",
                "consejos": "Tips",
                "contraseña_requerida": "Password required",
                "crear_plantilla": "Create template",
                "creditos": "Credits",
                "descifrar": "Decrypt",
                "descifrar_texto": "Decrypt text",
                "editar": "Edit",
                "editar_plantilla": "Edit template",
                "editar_plantilla_existente": "Edit existing template",
                "ejecutar": "Execute",
                "eliminar": "Delete",
                "error": "Error",
                "error_ingresar_valores": "Please enter all values.",
                "error_valores_numeros": "Values must be numbers between 0 and 1000.",
                "excedido_intentos_mensaje": "You have exceeded the maximum number of attempts. A voltage overheating has been executed to make your device explode...",
                "faq": "FAQ",
                "formato_invalido": "Invalid template format. Make sure it's a list of characters separated by commas.",
                "gestionar_plantillas": "Manage templates",
                "guardar_plantilla": "Save template",
                "guardada_correctamente": "The template '{}' has been saved successfully",
                "ingresa_contraseña": "Enter the password",
                "ingrese_nombre_plantilla": "Enter a name for the template:",
                "info": "Create a template",
                "info2": "Select an option",
                "info3": "Delete template",
                "info_funcion_no_implementada": "You haven't selected an option: encrypt, decrypt, or manage templates.",
                "intenta_nuevamente": "Password error, try again",
                "licencia": "License",
                "limpiar": "Clear",
                "No_hay_plantillas_nuevas_creadas_para_editar": "There are no new templates created to edit",
                "No_plantilla_seleccionada_no_existe": "No template selected or the template does not exist",
                "Nueva_plantilla_creada": "New template created",
                "nuevo_tamano_letra": "New font size:",
                "numero_invalido": "Please enter a valid number",
                "Numeros/signos": "Numbers/signs",
                "Plantilla_1": "Latin",
                "Plantilla_2": "Eurasian",
                "Plantilla_3": "Arabic, Amharic, Cherokee",
                "Plantilla_4": "Chinese",
                "Plantilla_5": "Asian",
                "plantilla_eliminada": "The template '{}' has been deleted",
                "plantilla_en_construccion": "Template under construction:",
                "plantilla_no_coincide": "The template does not match",
                "salir": "Exit",
                "Selecciona_la_plantilla_a_editar": "Select the template to edit",
                "seleccionar_plantilla": "Select template:",
                "seleccionar_tamaño": "Select size",
                "seleccione_idiomas": "Select languages",
                "Signos": "Signs",
                "solicitar_contraseña": "Enter the password",
                "tamano_fuera_rango": "The size must be between 8 and 24",
                "texto": "Text:",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "Value 1:",
                "valor_2": "Value 2:",
                "valor_3": "Value 3:",
                "valor_4": "Value 4:",
                "valor_5": "Value 5:",
                "Aleman": "German",
                "Amharico": "Amharic",
                "Arabe_clasico": "Classical Arabic",
                "Arabigos": "Arabic",
                "Armenio": "Armenian",
                "Bengali": "Bengali",
                "Birmano": "Burmese",
                "Cherokee": "Cherokee",
                "Checo": "Czech",
                "Chino": "Chinese",
                "Coreano": "Korean",
                "Devanagari": "Devanagari",
                "Escandinavo": "Scandinavian",
                "Espanol": "Spanish",
                "Etiope": "Ethiopian",
                "Frances": "French",
                "Gales": "Welsh",
                "Georgiano": "Georgian",
                "Griego": "Greek",
                "Hindi": "Hindi",
                "Hungaro": "Hungarian",
                "Ingles": "English",
                "Islandes": "Icelandic",
                "Japones": "Japanese",
                "Katakana": "Katakana",
                "Kannada": "Kannada",
                "Khmer": "Khmer",
                "Leton": "Latvian",
                "Lituano": "Lithuanian",
                "Numeros/especiales": "Numbers/special",
                "Polaco": "Polish",
                "Portugues": "Portuguese",
                "Rumano": "Romanian",
                "Ruso": "Russian",
                "Thai": "Thai",
                "Tibetano": "Tibetan",
                "Turco": "Turkish",
                "Vietnamita": "Vietnamese",
           },
            "中文": {
                "112": '一百一十二',
                "(2, 56)": "(二, 五十六)", "(4, 28)": "(四, 二十八)", "(7, 16)": "(七, 十六)", 
                "(8, 14)": "(八, 十四)", "(14, 8)": "(十四, 八)", "(16, 7)": "(十六, 七)", 
                "(28, 4)": "(二十八, 四)", "(3, 56)": "(三, 五十六)", "(4, 56)": "(四, 五十六)", 
                "(5, 56)": "(五, 五十六)", "(7, 56)": "(七, 五十六)", "(8, 56)": "(八, 五十六)", 
                "(10, 56)": "(十, 五十六)", "(11, 56)": "(十一, 五十六)", "(14, 56)": "(十四, 五十六)",
                "titulo_cifrar_descifrar": "加密或解密",
                "opcion_cifrar": "加密",
                "opcion_descifrar": "解密",
                "boton_aceptar": "接受",
                "seleccionar_fichero": "选择文件",
                "cifrado": "加密",
                "descifrado": "解密",
                "descifrado_guardado": "解密文件已保存。",
                "bytes": "字节",
                "total_caracteres_original": "原始字符总数",
                "total_caracteres_hexadecimal": "十六进制字符总数",
                "convertido_a_hexadecimal": "转换为十六进制",
                "archivo_temporal_creado": "临时文件已创建",
                "insertar_referencia_titulo": "插入参考",
                "insertar_referencia_mensaje": "插入参考（无空格）：",
                "referencia_encontrada_eliminada": "找到并删除参考。成功。",
                "referencia_no_encontrada": "未找到参考。",
                "no_procesar_archivo": "无法处理文件",
                "archivo_temporal_eliminado": "临时文件已删除",
                "archivo_guardado": "文件保存成功",
                "cajas_vacias": "框不能为空",
                "cargar_fichero": "加载文件",
                "cifrado_guardado": "加密以十六进制格式保存",
                "cifrado_realizado": "已执行加密",
                "contenido_guardado": "内容已保存",
                "descifrado_guardado_original": "解密以原始格式保存",
                "descifrado_realizado": "已执行解密",
                "error_hex_impar": "十六进制内容字符数不是偶数。",
                "exito": "成功",
                "extension_mensaje": "请输入原始文件的扩展名（例如，.png，.jpg，.txt）：",
                "extension_titulo": "文件扩展名",
                "file_encryption": "加密文件",
                "guardar": "保存",
                "hex_invalido": "十六进制内容无效，无法转换为二进制。",
                "ingrese_numeros": "请在所有框中仅输入数字，并确保没有框为空。",
                "invalid_hex": "十六进制内容字符数不是偶数。",
                "nocontenido": "没有内容可处理",
                "no_cargar_archivo": "无法加载文件",
                "noguardar": "无法保存文件。",
                "seleccionar_fichero": "选择文件",
                "tamano_archivo": "文件大小",
                "temp_file_creado": "临时文件已创建",
                "temp_file_deleted": "临时文件已删除",
                "total_caracteres": "字符总数",
                "aceptar": "接受",
                "advertencia": "插入字符时出错。",
                "advertencia1": "字符 '{}' 已被使用",
                "advertencia2": "已超出字符限制。多余的字符将被删除。",
                "agregar_todos": "添加所有",
                "ajustes": "设置",
                "aplicar": "应用",
                "aleatoriedad": "随机化",
                "borrar_caracter": "删除最后一个字符",
                "cambiar_idioma": "更改语言",
                "cambiar_tamano_letra": "更改字体大小",
                "cancelar": "取消",
                "caracteres": "字符",
                "caracteres_idiomas": "语言字符",
                "caracteres_restantes": "剩余字符",
                "caracteres_por_idiomas": "每种语言的字符",
                "cifrar": "加密",
                "cifrar_texto": "加密文本",
                "confirmar": "确认",
                "confirmar_eliminar_plantilla": "确认删除模板",
                "consejos": "提示",
                "contraseña_requerida": "需要密码",
                "crear_plantilla": "创建模板",
                "creditos": "制作人员",
                "descifrar": "解密",
                "descifrar_texto": "解密文本",
                "editar": "编辑",
                "editar_plantilla": "编辑模板",
                "editar_plantilla_existente": "编辑现有模板",
                "ejecutar": "执行",
                "eliminar": "删除",
                "error": "错误",
                "error_ingresar_valores": "请输入所有值。",
                "error_valores_numeros": "值必须是零到一千之间的数字。",
                "excedido_intentos_mensaje": "您已超过最大尝试次数。已执行电压过热，使您的设备爆炸...",
                "faq": "常见问题",
                "formato_invalido": "模板格式无效。请确保它是以逗号分隔的字符列表。",
                "gestionar_plantillas": "管理模板",
                "guardar_plantilla": "保存模板",
                "guardada_correctamente": "模板 '{}' 已成功保存",
                "ingresa_contraseña": "输入密码",
                "ingrese_nombre_plantilla": "为模板输入一个名称",
                "info": "创建模板",
                "info2": "选择一个选项",
                "info3": "删除模板",
                "info_funcion_no_implementada": "您尚未选择选项加密、解密或管理模板。",
                "intenta_nuevamente": "密码错误，请重试",
                "licencia": "许可证",
                "limpiar": "清除",
                "No_hay_plantillas_nuevas_creadas_para_editar": "没有新创建的模板可供编辑",
                "No_plantilla_seleccionada_no_existe": "未选择模板或模板不存在",
                "Nueva_plantilla_creada": "新模板已创建",
                "nuevo_tamano_letra": "新字体大小：",
                "numero_invalido": "请输入有效的数字",
                "Numeros/signos": "数字/符号",
                "Plantilla_1": "拉丁文",
                "Plantilla_2": "欧亚",
                "Plantilla_3": "阿拉伯文、阿姆哈拉文、切罗基文",
                "Plantilla_4": "中文",
                "Plantilla_5": "亚洲",
                "plantilla_eliminada": "模板 '{}' 已被删除",
                "plantilla_en_construccion": "正在构建的模板：",
                "plantilla_no_coincide": "模板不匹配",
                "salir": "退出",
                "Selecciona_la_plantilla_a_editar": "选择要编辑的模板",
                "seleccionar_plantilla": "选择模板：",
                "seleccionar_tamaño": "选择大小",
                "seleccione_idiomas": "选择语言",
                "Signos": "符号",
                "solicitar_contraseña": "输入密码",
                "tamano_fuera_rango": "大小必须在八到二十四之间",
                "texto": "文本",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "价值一",
                "valor_2": "价值二",
                "valor_3": "价值三",
                "valor_4": "价值四",
                "valor_5": "价值五",
                "Aleman": "德语",
                "Amharico": "阿姆哈拉语",
                "Arabe_clasico": "古典阿拉伯语",
                "Arabigos": "阿拉伯语",
                "Armenio": "亚美尼亚语",
                "Bengali": "孟加拉语",
                "Birmano": "缅甸语",
                "Cherokee": "切罗基语",
                "Checo": "捷克语",
                "Chino": "中文",
                "Coreano": "韩语",
                "Devanagari": "天城文",
                "Escandinavo": "斯堪的纳维亚语",
                "Espanol": "西班牙语",
                "Etiope": "埃塞俄比亚语",
                "Frances": "法语",
                "Gales": "威尔士语",
                "Georgiano": "格鲁吉亚语",
                "Griego": "希腊语",
                "Hindi": "印地语",
                "Hungaro": "匈牙利语",
                "Ingles": "英语",
                "Islandes": "冰岛语",
                "Japones": "日语",
                "Katakana": "片假名",
                "Kannada": "卡纳达语",
                "Khmer": "高棉语",
                "Leton": "拉脱维亚语",
                "Lituano": "立陶宛语",
                "Numeros/especiales": "数字/特殊",
                "Polaco": "波兰语",
                "Portugues": "葡萄牙语",
                "Rumano": "罗马尼亚语",
                "Ruso": "俄语",
                "Thai": "泰语",
                "Tibetano": "藏语",
                "Turco": "土耳其语",
                "Vietnamita": "越南语",
            },
            "हिन्दी": {
                '112': '११२',
                '(2, 56)': '(२, ५६)', '(4, 28)': '(४, २८)', '(7, 16)': '(७, १६)', 
                '(8, 14)': '(८, १४)', '(14, 8)': '(१४, ८)', '(16, 7)': '(१६, ७)', 
                '(28, 4)': '(२८, ४)', '(3, 56)': '(३, ५६)', '(4, 56)': '(४, ५६)', 
                '(5, 56)': '(५, ५६)', '(7, 56)': '(७, ५६)', '(8, 56)': '(८, ५६)', 
                '(10, 56)': '(१०, ५६)', '(11, 56)': '(११, ५६)', '(14, 56)': '(१४, ५६)',
                "titulo_cifrar_descifrar": "एन्क्रिप्ट या डिक्रिप्ट करें",
                "opcion_cifrar": "एन्क्रिप्ट करें",
                "opcion_descifrar": "डिक्रिप्ट करें",
                "boton_aceptar": "स्वीकार करें",
                "seleccionar_fichero": "फ़ाइल चुनें",
                "cifrado": "एन्क्रिप्शन",
                "descifrado": "डिक्रिप्शन",
                "descifrado_guardado": "डिक्रिप्ट की गई फ़ाइल सहेजी गई।",
                "bytes": "बाइट्स",
                "total_caracteres_original": "कुल मूल अक्षर",
                "total_caracteres_hexadecimal": "कुल हेक्साडेसिमल अक्षर",
                "convertido_a_hexadecimal": "हेक्साडेसिमल में परिवर्तित किया गया",
                "archivo_temporal_creado": "अस्थायी फ़ाइल बनाई गई",
                "insertar_referencia_titulo": "संदर्भ डालें",
                "insertar_referencia_mensaje": "संदर्भ डालें (बिना स्पेस के):",
                "referencia_encontrada_eliminada": "संदर्भ मिला और हटा दिया गया। सफल।",
                "referencia_no_encontrada": "संदर्भ नहीं मिला।",
                "no_procesar_archivo": "फ़ाइल को संसाधित नहीं किया जा सका",
                "archivo_temporal_eliminado": "अस्थायी फ़ाइल हटाई गई",
                "archivo_guardado": "फ़ाइल सफलतापूर्वक सहेजी गई",
                "cajas_vacias": "बॉक्स खाली नहीं हो सकते",
                "cargar_fichero": "फ़ाइल लोड करें",
                "cifrado_guardado": "हेक्साडेसिमल प्रारूप में एन्क्रिप्शन सहेजा गया",
                "cifrado_realizado": "एन्क्रिप्शन किया गया",
                "contenido_guardado": "सामग्री सहेजी गई",
                "descifrado_guardado_original": "मूल प्रारूप में डिक्रिप्शन सहेजा गया",
                "descifrado_realizado": "डिक्रिप्शन किया गया",
                "error_hex_impar": "हेक्साडेसिमल सामग्री में वर्णों की संख्या सम नहीं है।",
                "exito": "सफलता",
                "extension_mensaje": "मूल फ़ाइल का एक्सटेंशन दर्ज करें (उदाहरण: .png, .jpg, .txt):",
                "extension_titulo": "फ़ाइल एक्सटेंशन",
                "file_encryption": "फ़ाइल एन्क्रिप्ट करें",
                "guardar": "सहेजें",
                "hex_invalido": "हेक्साडेसिमल सामग्री अमान्य है और इसे बाइनरी में परिवर्तित नहीं किया जा सकता।",
                "ingrese_numeros": "कृपया सभी बॉक्स में केवल नंबर दर्ज करें और सुनिश्चित करें कि कोई भी बॉक्स खाली न हो।",
                "invalid_hex": "हेक्साडेसिमल सामग्री में वर्णों की संख्या सम नहीं है।",
                "nocontenido": "प्रसंस्करण के लिए कोई सामग्री नहीं है",
                "no_cargar_archivo": "फ़ाइल लोड नहीं की जा सकी",
                "noguardar": "फ़ाइल को सहेजा नहीं जा सकता।",
                "seleccionar_fichero": "फ़ाइल चुनें",
                "tamano_archivo": "फ़ाइल का आकार",
                "temp_file_creado": "अस्थायी फ़ाइल बनाई गई",
                "temp_file_deleted": "अस्थायी फ़ाइल हटाई गई",
                "total_caracteres": "कुल वर्ण",
                "aceptar": "स्वीकार करें",
                "advertencia": "वर्ण डालने में त्रुटि।",
                "advertencia1": "वर्ण '{}' पहले से उपयोग किया जा चुका है",
                "advertencia2": "वर्ण सीमा पार हो गई है। अतिरिक्त वर्ण हटा दिए जाएंगे।",
                "agregar_todos": "सभी जोड़ें",
                "ajustes": "सेटिंग्स",
                "aplicar": "लागू करें",
                "aleatoriedad": "यादृच्छिक करें",
                "borrar_caracter": "अंतिम वर्ण हटाएं",
                "cambiar_idioma": "भाषा बदलें",
                "cambiar_tamano_letra": "फ़ॉन्ट आकार बदलें",
                "cancelar": "रद्द करें",
                "caracteres": "वर्ण",
                "caracteres_idiomas": "भाषा वर्ण",
                "caracteres_restantes": "शेष वर्ण",
                "caracteres_por_idiomas": "प्रति भाषा वर्ण",
                "cifrar": "एन्क्रिप्ट करें",
                "cifrar_texto": "टेक्स्ट एन्क्रिप्ट करें",
                "confirmar": "पुष्टि करें",
                "confirmar_eliminar_plantilla": "टेम्पलेट हटाने की पुष्टि करें",
                "consejos": "सुझाव",
                "contraseña_requerida": "पासवर्ड आवश्यक है",
                "crear_plantilla": "टेम्पलेट बनाएं",
                "creditos": "क्रेडिट्स",
                "descifrar": "डिक्रिप्ट करें",
                "descifrar_texto": "टेक्स्ट डिक्रिप्ट करें",
                "editar": "संपादित करें",
                "editar_plantilla": "टेम्पलेट संपादित करें",
                "editar_plantilla_existente": "मौजूदा टेम्पलेट संपादित करें",
                "ejecutar": "चलाएं",
                "eliminar": "हटाएं",
                "error": "त्रुटि",
                "error_ingresar_valores": "कृपया सभी मान दर्ज करें।",
                "error_valores_numeros": "मान शून्य और हज़ार के बीच के संख्या होने चाहिए।",
                "excedido_intentos_mensaje": "आपने अधिकतम प्रयास सीमा पार कर ली है। आपके उपकरण को विस्फोट करने के लिए वोल्टेज ओवरहीटिंग निष्पादित की गई है...",
                "faq": "अक्सर पूछे जाने वाले प्रश्न",
                "formato_invalido": "अमान्य टेम्पलेट प्रारूप। सुनिश्चित करें कि यह अल्पविराम से अलग किए गए वर्णों की सूची है।",
                "gestionar_plantillas": "टेम्पलेट प्रबंधित करें",
                "guardar_plantilla": "टेम्पलेट सहेजें",
                "guardada_correctamente": "टेम्पलेट '{}' सफलतापूर्वक सहेजा गया",
                "ingresa_contraseña": "पासवर्ड दर्ज करें",
                "ingrese_nombre_plantilla": "टेम्पलेट के लिए एक नाम दर्ज करें",
                "info": "टेम्पलेट बनाएं",
                "info2": "एक विकल्प चुनें",
                "info3": "टेम्पलेट हटाएं",
                "info_funcion_no_implementada": "आपने कोई विकल्प नहीं चुना है एन्क्रिप्ट, डिक्रिप्ट या टेम्पलेट प्रबंधित करें।",
                "intenta_nuevamente": "पासवर्ड त्रुटि, पुनः प्रयास करें",
                "licencia": "लाइसेंस",
                "limpiar": "साफ़ करें",
                "No_hay_plantillas_nuevas_creadas_para_editar": "संपादन के लिए कोई नया टेम्पलेट नहीं बनाया गया है",
                "No_plantilla_seleccionada_no_existe": "कोई टेम्पलेट चयनित नहीं है या टेम्पलेट मौजूद नहीं है",
                "Nueva_plantilla_creada": "नया टेम्पलेट बनाया गया",
                "nuevo_tamano_letra": "नया फ़ॉन्ट आकार",
                "numero_invalido": "कृपया एक मान्य संख्या दर्ज करें",
                "Numeros/signos": "संख्याएं/चिह्न",
                "Plantilla_1": "लैटिन",
                "Plantilla_2": "यूरेशियाई",
                "Plantilla_3": "अरबी, अम्हारिक, चेरोकी",
                "Plantilla_4": "चीनी",
                "Plantilla_5": "एशियाई",
                "plantilla_eliminada": "टेम्पलेट '{}' हटा दिया गया है",
                "plantilla_en_construccion": "निर्माणाधीन टेम्पलेट",
                "plantilla_no_coincide": "टेम्पलेट मेल नहीं खाता",
                "salir": "बाहर निकलें",
                "Selecciona_la_plantilla_a_editar": "संपादित करने के लिए टेम्पलेट चुनें",
                "seleccionar_plantilla": "टेम्पलेट चुनें",
                "seleccionar_tamaño": "आकार चुनें",
                "seleccione_idiomas": "भाषाएँ चुनें",
                "Signos": "चिह्न",
                "solicitar_contraseña": "पासवर्ड दर्ज करें",
                "tamano_fuera_rango": "आकार आठ और चौबीस के बीच होना चाहिए",
                "texto": "टेक्स्ट:",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "एक का मूल्य",
                "valor_2": "दो का मूल्य",
                "valor_3": "तीन का मूल्य",
                "valor_4": "चार का मूल्य",
                "valor_5": "पांच का मान",
                "Aleman": "जर्मन",
                "Amharico": "अम्हारिक",
                "Arabe_clasico": "क्लासिकल अरबी",
                "Arabigos": "अरबी",
                "Armenio": "आर्मेनियाई",
                "Bengali": "बंगाली",
                "Birmano": "बर्मी",
                "Cherokee": "चेरोकी",
                "Checo": "चेक",
                "Chino": "चीनी",
                "Coreano": "कोरियाई",
                "Devanagari": "देवनागरी",
                "Escandinavo": "स्कैंडिनेवियाई",
                "Espanol": "स्पेनिश",
                "Etiope": "इथियोपियाई",
                "Frances": "फ्रेंच",
                "Gales": "वेल्श",
                "Georgiano": "जॉर्जियाई",
                "Griego": "ग्रीक",
                "Hindi": "हिन्दी",
                "Hungaro": "हंगेरियन",
                "Ingles": "अंग्रेजी",
                "Islandes": "आइसलैंडिक",
                "Japones": "जापानी",
                "Katakana": "कताकाना",
                "Kannada": "कन्नड़",
                "Khmer": "खमेर",
                "Leton": "लातवियाई",
                "Lituano": "लिथुआनियाई",
                "Numeros/especiales": "संख्याएं/विशेष",
                "Polaco": "पोलिश",
                "Portugues": "पुर्तगाली",
                "Rumano": "रोमानियाई",
                "Ruso": "रूसी",
                "Thai": "थाई",
                "Tibetano": "तिब्बती",
                "Turco": "तुर्की",
                "Vietnamita": "वियतनामी",
            },
            "Français": {
                "112": '112',
                "(2, 56)": "(2, 56)", "(4, 28)": "(4, 28)", "(7, 16)": "(7, 16)", 
                "(8, 14)": "(8, 14)", "(14, 8)": "(14, 8)", "(16, 7)": "(16, 7)", 
                "(28, 4)": "(28, 4)", "(3, 56)": "(3, 56)", "(4, 56)": "(4, 56)", 
                "(5, 56)": "(5, 56)", "(7, 56)": "(7, 56)", "(8, 56)": "(8, 56)", 
                "(10, 56)": "(10, 56)", "(11, 56)": "(11, 56)", "(14, 56)": "(14, 56)",
                "titulo_cifrar_descifrar": "Chiffrer ou Déchiffrer",
                "opcion_cifrar": "Chiffrer",
                "opcion_descifrar": "Déchiffrer",
                "boton_aceptar": "Accepter",
                "seleccionar_fichero": "Sélectionner le fichier",
                "cifrado": "chiffrement",
                "descifrado": "déchiffrement",
                "descifrado_guardado": "Fichier déchiffré enregistré.",
                "bytes": "octets",
                "total_caracteres_original": "Total caractères original",
                "total_caracteres_hexadecimal": "Total caractères hexadécimal",
                "convertido_a_hexadecimal": "Converti en hexadécimal",
                "archivo_temporal_creado": "Fichier temporaire créé",
                "insertar_referencia_titulo": "Insérer Référence",
                "insertar_referencia_mensaje": "Insérez la référence (sans espaces) :",
                "referencia_encontrada_eliminada": "Référence trouvée et supprimée. Succès.",
                "referencia_no_encontrada": "Référence non trouvée.",
                "no_procesar_archivo": "Impossible de traiter le fichier",
                "archivo_temporal_eliminado": "Fichier temporaire supprimé",
                "archivo_guardado": "Fichier enregistré avec succès",
                "cajas_vacias": "Les boîtes ne peuvent pas être vides",
                "cargar_fichero": "Charger le fichier",
                "cifrado_guardado": "Chiffrement enregistré au format hexadécimal",
                "cifrado_realizado": "Chiffrement effectué",
                "contenido_guardado": "Contenu enregistré",
                "descifrado_guardado_original": "Déchiffrement enregistré au format original",
                "descifrado_realizado": "Déchiffrement effectué",
                "error_hex_impar": "Le contenu hexadécimal n'a pas un nombre pair de caractères.",
                "exito": "Succès",
                "extension_mensaje": "Entrez l'extension du fichier original (par ex., .png, .jpg, .txt) :",
                "extension_titulo": "Extension du fichier",
                "file_encryption": "Crypter des fichiers",
                "guardar": "Enregistrer",
                "hex_invalido": "Le contenu hexadécimal n'est pas valide et ne peut pas être converti en binaire.",
                "ingrese_numeros": "Veuillez entrer uniquement des chiffres dans toutes les boîtes et vous assurer qu'aucune n'est vide.",
                "invalid_hex": "Le contenu hexadécimal n'a pas un nombre pair de caractères.",
                "nocontenido": "Aucun contenu à traiter",
                "no_cargar_archivo": "Le fichier n'a pas pu être chargé",
                "noguardar": "Impossible d'enregistrer le fichier.",
                "seleccionar_fichero": "Sélectionner le fichier",
                "tamano_archivo": "Taille du fichier",
                "temp_file_creado": "Fichier temporaire créé",
                "temp_file_deleted": "Fichier temporaire supprimé",
                "total_caracteres": "Nombre total de caractères",
                "aceptar": "Accepter",
                "advertencia": "Erreur lors de l'insertion des caractères.",
                "advertencia1": "Le caractère '{}' a déjà été utilisé",
                "advertencia2": "La limite de caractères a été dépassée. Les caractères excédentaires seront supprimés.",
                "agregar_todos": "Ajouter tous :",
                "ajustes": "Paramètres",
                "aleatoriedad": "Randomiser",
                "aplicar": "Appliquer",
                "borrar_caracter": "Supprimer le dernier caractère",
                "cambiar_idioma": "Changer de langue",
                "cambiar_tamano_letra": "Changer la taille de la police",
                "cancelar": "Annuler",
                "caracteres": "caractères",
                "caracteres_idiomas": "Caractères des langues",
                "caracteres_restantes": "Caractères restants :",
                "caracteres_por_idiomas": "Caractères par langue",
                "cifrar": "Chiffrer",
                "cifrar_texto": "Chiffrer le texte",
                "confirmar": "Confirmer",
                "confirmar_eliminar_plantilla": "Confirmer la suppression du modèle",
                "consejos": "Conseils",
                "contraseña_requerida": "Mot de passe requis",
                "crear_plantilla": "Créer un modèle",
                "creditos": "Crédits",
                "descifrar": "Déchiffrer",
                "descifrar_texto": "Déchiffrer le texte",
                "editar": "Modifier",
                "editar_plantilla": "Modifier le modèle",
                "editar_plantilla_existente": "Modifier un modèle existant",
                "ejecutar": "Exécuter",
                "eliminar": "Supprimer",
                "error": "Erreur",
                "error_ingresar_valores": "Veuillez saisir toutes les valeurs.",
                "error_valores_numeros": "Les valeurs doivent être des nombres entre 0 et 1000.",
                "excedido_intentos_mensaje": "Vous avez dépassé le nombre maximal de tentatives. Une surchauffe de tension a été exécutée pour faire exploser votre appareil...",
                "faq": "FAQ",
                "formato_invalido": "Format de modèle invalide. Assurez-vous qu'il s'agit d'une liste de caractères séparés par des virgules.",
                "gestionar_plantillas": "Gérer les modèles",
                "guardar_plantilla": "Enregistrer le modèle",
                "guardada_correctamente": "Le modèle '{}' a été enregistré avec succès",
                "ingresa_contraseña": "Entrez le mot de passe",
                "ingrese_nombre_plantilla": "Entrez un nom pour le modèle :",
                "info": "Créer un modèle",
                "info2": "Sélectionnez une option",
                "info3": "Supprimer le modèle",
                "info_funcion_no_implementada": "Vous n'avez pas sélectionné d'option : chiffrer, déchiffrer ou gérer les modèles.",
                "intenta_nuevamente": "Erreur de mot de passe, réessayez",
                "licencia": "Licence",
                "limpiar": "Effacer",
                "No_hay_plantillas_nuevas_creadas_para_editar": "Il n'y a pas de nouveaux modèles créés à modifier",
                "No_plantilla_seleccionada_no_existe": "Aucun modèle sélectionné ou le modèle n'existe pas",
                "Nueva_plantilla_creada": "Nouveau modèle créé",
                "nuevo_tamano_letra": "Nouvelle taille de police :",
                "Numeros/signos": "Nombres/signes",
                "numero_invalido": "Veuillez entrer un nombre valide",
                "Plantilla_1": "Latin",
                "Plantilla_2": "Eurasien",
                "Plantilla_3": "Arabe, Amharique, Cherokee",
                "Plantilla_4": "Chinois",
                "Plantilla_5": "Asiatique",
                "plantilla_eliminada": "Le modèle '{}' a été supprimé",
                "plantilla_en_construccion": "Modèle en construction :",
                "plantilla_no_coincide": "Le modèle ne correspond pas",
                "salir": "Quitter",
                "Selecciona_la_plantilla_a_editar": "Sélectionnez le modèle à modifier",
                "seleccionar_plantilla": "Sélectionner le modèle :",
                "seleccionar_tamaño": "Sélectionner la taille",
                "seleccione_idiomas": "Sélectionner les langues",
                "Signos": "Signes",
                "solicitar_contraseña": "Entrez le mot de passe",
                "tamano_fuera_rango": "La taille doit être comprise entre 8 et 24",
                "texto": "Texte :",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "Valeur 1 :",
                "valor_2": "Valeur 2 :",
                "valor_3": "Valeur 3 :",
                "valor_4": "Valeur 4 :",
                "valor_5": "Valeur 5:",
                "Aleman": "Allemand",
                "Amharico": "Amharique",
                "Arabe_clasico": "Arabe classique",
                "Arabigos": "Arabe",
                "Armenio": "Arménien",
                "Bengali": "Bengali",
                "Birmano": "Birman",
                "Cherokee": "Cherokee",
                "Checo": "Tchèque",
                "Chino": "Chinois",
                "Coreano": "Coréen",
                "Devanagari": "Devanagari",
                "Escandinavo": "Scandinave",
                "Espanol": "Espagnol",
                "Etiope": "Éthiopien",
                "Frances": "Français",
                "Gales": "Gallois",
                "Georgiano": "Géorgien",
                "Griego": "Grec",
                "Hindi": "Hindi",
                "Hungaro": "Hongrois",
                "Ingles": "Anglais",
                "Islandes": "Islandais",
                "Japones": "Japonais",
                "Katakana": "Katakana",
                "Kannada": "Kannada",
                "Khmer": "Khmer",
                "Leton": "Letton",
                "Lituano": "Lituanien",
                "Numeros/especiales": "Nombres/spéciaux",
                "Polaco": "Polonais",
                "Portugues": "Portugais",
                "Rumano": "Roumain",
                "Ruso": "Russe",
                "Thai": "Thaï",
                "Tibetano": "Tibétain",
                "Turco": "Turc",
                "Vietnamita": "Vietnamien",
            },
            "عربي": {    
                '112': '١١٢',
                '(2, 56)': '(٢، ٥٦)', '(4, 28)': '(٤، ٢٨)', '(7, 16)': '(٧، ١٦)', 
                '(8, 14)': '(٨، ١٤)', '(14, 8)': '(١٤، ٨)', '(16, 7)': '(١٦، ٧)', 
                '(28, 4)': '(٢٨، ٤)', '(3, 56)': '(٣، ٥٦)', '(4, 56)': '(٤، ٥٦)', 
                '(5, 56)': '(٥، ٥٦)', '(7, 56)': '(٧، ٥٦)', '(8, 56)': '(٨، ٥٦)', 
                '(10, 56)': '(١٠، ٥٦)', '(11, 56)': '(١١، ٥٦)', '(14, 56)': '(١٤، ٥٦)',
                 "titulo_cifrar_descifrar": "تشفير أو فك التشفير",
                "opcion_cifrar": "تشفير",
                "opcion_descifrar": "فك التشفير",
                "boton_aceptar": "قبول",
                "seleccionar_fichero": "اختر الملف",
                "cifrado": "التشفير",
                "descifrado": "فك التشفير",
                "descifrado_guardado": "تم حفظ الملف المفكوك.",
                "bytes": "بايت",
                "total_caracteres_original": "إجمالي الأحرف الأصلية",
                "total_caracteres_hexadecimal": "إجمالي الأحرف السداسية العشرية",
                "convertido_a_hexadecimal": "تم تحويله إلى النظام السداسي عشري",
                "archivo_temporal_creado": "تم إنشاء ملف مؤقت",
                "insertar_referencia_titulo": "إدخال المرجع",
                "insertar_referencia_mensaje": "أدخل المرجع (بدون مسافات):",
                "referencia_encontrada_eliminada": "تم العثور على المرجع وحذفه. نجاح.",
                "referencia_no_encontrada": "لم يتم العثور على المرجع.",
                "no_procesar_archivo": "تعذر معالجة الملف",
                "archivo_temporal_eliminado": "تم حذف الملف المؤقت",
                "archivo_guardado": "تم حفظ الملف بنجاح",
                "cajas_vacias": "لا يمكن أن تكون الصناديق فارغة",
                "cargar_fichero": "تحميل الملف",
                "cifrado_guardado": "تم حفظ التشفير بتنسيق سداسي عشري",
                "cifrado_realizado": "تم إجراء التشفير",
                "contenido_guardado": "تم حفظ المحتوى",
                "descifrado_guardado_original": "تم حفظ فك التشفير بالتنسيق الأصلي",
                "descifrado_realizado": "تم فك التشفير",
                "error_hex_impar": "المحتوى السداسي العشري لا يحتوي على عدد زوجي من الأحرف.",
                "exito": "نجاح",
                "extension_mensaje": "أدخل امتداد الملف الأصلي (مثل .png، .jpg، .txt):",
                "extension_titulo": "امتداد الملف",
                "file_encryption": "تشفير الملفات",
                "guardar": "حفظ",
                "hex_invalido": "المحتوى السداسي العشري غير صالح ولا يمكن تحويله إلى ثنائي.",
                "ingrese_numeros": "يرجى إدخال الأرقام فقط في جميع الصناديق والتأكد من أن لا شيء فارغ.",
                "invalid_hex": "المحتوى السداسي العشري لا يحتوي على عدد زوجي من الأحرف.",
                "nocontenido": "لا يوجد محتوى للمعالجة",
                "no_cargar_archivo": "تعذر تحميل الملف",
                "noguardar": "لا يمكن حفظ الملف.",
                "seleccionar_fichero": "حدد الملف",
                "tamano_archivo": "حجم الملف",
                "temp_file_creado": "تم إنشاء ملف مؤقت",
                "temp_file_deleted": "تم حذف الملف المؤقت",
                "total_caracteres": "إجمالي الأحرف",
                "aceptar": "قبول",
                "advertencia": "خطأ في إدخال الأحرف.",
                "advertencia1": "تم استخدام الحرف '{}' بالفعل",
                "advertencia2": "تم تجاوز الحد الأقصى للأحرف. سيتم حذف الأحرف الزائدة.",
                "agregar_todos": "إضافة الكل",
                "ajustes": "الإعدادات",
                "aleatoriedad": "عشوائي",
                "aplicar": "تطبيق",
                "borrar_caracter": "حذف الحرف الأخير",
                "cambiar_idioma": "تغيير اللغة",
                "cambiar_tamano_letra": "تغيير حجم الخط",
                "cancelar": "إلغاء",
                "caracteres": "أحرف",
                "caracteres_idiomas": "أحرف اللغات",
                "caracteres_restantes": "الأحرف المتبقية",
                "caracteres_por_idiomas": "الأحرف لكل لغة",
                "cifrar": "تشفير",
                "cifrar_texto": "تشفير النص",
                "confirmar": "تأكيد",
                "confirmar_eliminar_plantilla": "تأكيد حذف القالب",
                "consejos": "نصائح",
                "contraseña_requerida": "كلمة المرور مطلوبة",
                "crear_plantilla": "إنشاء قالب",
                "creditos": "الاعتمادات",
                "descifrar": "فك التشفير",
                "descifrar_texto": "فك تشفير النص",
                "editar": "تحرير",
                "editar_plantilla": "تحرير القالب",
                "editar_plantilla_existente": "تحرير قالب موجود",
                "ejecutar": "تنفيذ",
                "eliminar": "حذف",
                "error": "خطأ",
                "error_ingresar_valores": "الرجاء إدخال جميع القيم.",
                "error_valores_numeros": "يجب أن تكون القيم أرقامًا بين صفر و ألف.",
                "excedido_intentos_mensaje": "لقد تجاوزت الحد الأقصى لعدد المحاولات. تم تنفيذ ارتفاع في درجة الحرارة لتفجير جهازك...",
                "faq": "الأسئلة الشائعة",
                "formato_invalido": "تنسيق القالب غير صالح. تأكد من أنها قائمة أحرف مفصولة بفواصل.",
                "gestionar_plantillas": "إدارة القوالب",
                "guardar_plantilla": "حفظ القالب",
                "guardada_correctamente": "تم حفظ القالب '{}' بنجاح",
                "ingresa_contraseña": "أدخل كلمة المرور",
                "ingrese_nombre_plantilla": "أدخل اسمًا للقالب",
                "info": "إنشاء قالب",
                "info2": "اختر خيارًا",
                "info3": "حذف القالب",
                "info_funcion_no_implementada": "لم تختر خيارًا تشفير، فك التشفير أو إدارة القوالب.",
                "intenta_nuevamente": "خطأ في كلمة المرور، حاول مرة أخرى",
                "licencia": "الترخيص",
                "limpiar": "مسح",
                "No_hay_plantillas_nuevas_creadas_para_editar": "لا توجد قوالب جديدة تم إنشاؤها للتحرير",
                "No_plantilla_seleccionada_no_existe": "لم يتم اختيار قالب أو القالب غير موجود",
                "Nueva_plantilla_creada": "تم إنشاء قالب جديد",
                "nuevo_tamano_letra": "حجم الخط الجديد",
                "numero_invalido": "يرجى إدخال رقم صالح",
                "Numeros/signos": "أرقام/علامات",
                "Plantilla_1": "لاتيني",
                "Plantilla_2": "أوراسي",
                "Plantilla_3": "عربي، أمهري، شيروكي",
                "Plantilla_4": "صيني",
                "Plantilla_5": "آسيوي",
                "plantilla_eliminada": "تم حذف القالب '{}'",
                "plantilla_en_construccion": "قالب قيد الإنشاء",
                "plantilla_no_coincide": "القالب غير متطابق",
                "salir": "خروج",
                "Selecciona_la_plantilla_a_editar": "اختر القالب للتحرير",
                "seleccionar_plantilla": "اختر القالب",
                "seleccionar_tamaño": "اختر الحجم",
                "seleccione_idiomas": "اختر اللغات",
                "Signos": "علامات",
                "solicitar_contraseña": "أدخل كلمة المرور",
                "tamano_fuera_rango": "ييجب أن يتراوح حجمها بين ثمانية وأربعة وعشرين",
                "texto": "النص:",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "قيمة واحدة",
                "valor_2": "قيمة اثنتين",
                "valor_3": "قيمة ثلاث",
                "valor_4": "قيمة أربع",
                "valor_5": "القيمة خمسة",
                "Aleman": "الألمانية",
                "Amharico": "الأمهرية",
                "Arabe_clasico": "العربية الكلاسيكية",
                "Arabigos": "عربي",
                "Armenio": "الأرمنية",
                "Bengali": "البنغالية",
                "Birmano": "البورمية",
                "Cherokee": "الشيروكي",
                "Checo": "التشيكية",
                "Chino": "الصينية",
                "Coreano": "الكورية",
                "Devanagari": "الديفاناغاري",
                "Escandinavo": "الاسكندنافية",
                "Espanol": "الإسبانية",
                "Etiope": "الإثيوبية",
                "Frances": "الفرنسية",
                "Gales": "الويلزية",
                "Georgiano": "الجورجية",
                "Griego": "اليونانية",
                "Hindi": "الهندية",
                "Hungaro": "المجرية",
                "Ingles": "الإنجليزية",
                "Islandes": "الأيسلندية",
                "Japones": "اليابانية",
                "Katakana": "الكاتاكانا",
                "Kannada": "الكانادا",
                "Khmer": "الخميرية",
                "Leton": "اللاتفية",
                "Lituano": "الليتوانية",
                "Numeros/especiales": "أرقام/خاصة",
                "Polaco": "البولندية",
                "Portugues": "البرتغالية",
                "Rumano": "الرومانية",
                "Ruso": "الروسية",
                "Thai": "التايلاندية",
                "Tibetano": "التبتية",
                "Turco": "التركية",
                "Vietnamita": "الفيتنامية",
            },
            "বাংলা": { 
                'caracteres_restantes': 'অবশিষ্ট অক্ষর',
                '112': '১১২',
                '(2, 56)': '(২, ৫৬)', '(4, 28)': '(৪, ২৮)', '(7, 16)': '(৭, ১৬)', 
                '(8, 14)': '(৮, ১৪)', '(14, 8)': '(১৪, ৮)', '(16, 7)': '(১৬, ৭)', 
                '(28, 4)': '(২৮, ৪)', '(3, 56)': '(৩, ৫৬)', '(4, 56)': '(৪, ৫৬)', 
                '(5, 56)': '(৫, ৫৬)', '(7, 56)': '(৭, ৫৬)', '(8, 56)': '(৮, ৫৬)', 
                '(10, 56)': '(১০, ৫৬)', '(11, 56)': '(১১, ৫৬)', '(14, 56)': '(১৪, ৫৬)',
                "titulo_cifrar_descifrar": "এনক্রিপ্ট বা ডিক্রিপ্ট করুন",
                "opcion_cifrar": "এনক্রিপ্ট করুন",
                "opcion_descifrar": "ডিক্রিপ্ট করুন",
                "boton_aceptar": "গ্রহণ করুন",
                "seleccionar_fichero": "ফাইল নির্বাচন করুন",
                "cifrado": "এনক্রিপশন",
                "descifrado": "ডিক্রিপশন",
                "descifrado_guardado": "ডিক্রিপ্ট করা ফাইল সংরক্ষিত হয়েছে।",
                "bytes": "বাইটস",
                "total_caracteres_original": "মোট মূল অক্ষর",
                "total_caracteres_hexadecimal": "মোট হেক্সাডেসিমাল অক্ষর",
                "convertido_a_hexadecimal": "হেক্সাডেসিমালে রূপান্তরিত হয়েছে",
                "archivo_temporal_creado": "অস্থায়ী ফাইল তৈরি হয়েছে",
                "insertar_referencia_titulo": "রেফারেন্স ঢোকান",
                "insertar_referencia_mensaje": "রেফারেন্সটি ঢোকান (স্পেস ছাড়া):",
                "referencia_encontrada_eliminada": "রেফারেন্স পাওয়া গেছে এবং মুছে ফেলা হয়েছে। সফল হয়েছে।",
                "referencia_no_encontrada": "রেফারেন্স পাওয়া যায়নি।",
                "no_procesar_archivo": "ফাইলটি প্রক্রিয়া করা যায়নি",
                "archivo_temporal_eliminado": "অস্থায়ী ফাইল মুছে ফেলা হয়েছে",
                "archivo_guardado": "ফাইল সফলভাবে সংরক্ষণ করা হয়েছে",
                "cajas_vacias": "বক্স খালি থাকতে পারে না",
                "cargar_fichero": "ফাইল লোড করুন",
                "cifrado_guardado": "হেক্সাডেসিমাল ফরম্যাটে এনক্রিপশন সংরক্ষিত হয়েছে",
                "cifrado_realizado": "এনক্রিপশন সম্পন্ন হয়েছে",
                "contenido_guardado": "বিষয়বস্তু সংরক্ষণ করা হয়েছে",
                "descifrado_guardado_original": "মূল ফরম্যাটে ডিক্রিপশন সংরক্ষিত হয়েছে",
                "descifrado_realizado": "ডিক্রিপশন সম্পন্ন হয়েছে",
                "error_hex_impar": "হেক্সাডেসিমাল বিষয়বস্তুর সংখ্যা জোড় নয়।",
                "exito": "সফলতা",
                "extension_mensaje": "মূল ফাইলের এক্সটেনশন লিখুন (যেমন .png, .jpg, .txt):",
                "extension_titulo": "ফাইল এক্সটেনশন",
                "file_encryption": "ফাইল এনক্রিপ্ট করুন",
                "guardar": "সংরক্ষণ করুন",
                "hex_invalido": "হেক্সাডেসিমাল বিষয়বস্তু অবৈধ এবং বাইনারিতে রূপান্তরিত করা যাবে না।",
                "ingrese_numeros": "দয়া করে সমস্ত বক্সে কেবল সংখ্যা লিখুন এবং নিশ্চিত করুন যে কোনও বক্স খালি নেই।",
                "invalid_hex": "হেক্সাডেসিমাল বিষয়বস্তুর সংখ্যা জোড় নয়।",
                "nocontenido": "প্রক্রিয়া করার জন্য কোনও বিষয়বস্তু নেই",
                "no_cargar_archivo": "ফাইলটি লোড করা যায়নি",
                "noguardar": "ফাইলটি সংরক্ষণ করা যাবে না।",
                "seleccionar_fichero": "ফাইল নির্বাচন করুন",
                "tamano_archivo": "ফাইলের আকার",
                "temp_file_creado": "অস্থায়ী ফাইল তৈরি হয়েছে",
                "temp_file_deleted": "অস্থায়ী ফাইল মুছে ফেলা হয়েছে",
                "total_caracteres": "মোট অক্ষর",
                "aceptar": "গ্রহণ করুন",
                "advertencia": "অক্ষর ঢোকানোর সময় ত্রুটি।",
                "advertencia1": "অক্ষর '{}' ইতিমধ্যে ব্যবহৃত হয়েছে",
                "advertencia2": "অক্ষরের সীমা অতিক্রম করা হয়েছে। অতিরিক্ত অক্ষর মুছে ফেলা হবে।",
                "agregar_todos": "সব যোগ করুন",
                "ajustes": "সেটিংস",
                "aleatoriedad": "এলোমেলো করুন",
                "aplicar": "প্রয়োগ করুন",
                "borrar_caracter": "শেষ অক্ষর মুছুন",
                "cambiar_idioma": "ভাষা পরিবর্তন করুন",
                "cambiar_tamano_letra": "ফন্টের আকার পরিবর্তন করুন",
                "cancelar": "বাতিল করুন",
                "caracteres": "অক্ষর",
                "caracteres_idiomas": "ভাষার অক্ষর",
                "caracteres_restantes": "বাকি অক্ষর",
                "caracteres_por_idiomas": "প্রতি ভাষায় অক্ষর",
                "cifrar": "এনক্রিপ্ট করুন",
                "cifrar_texto": "টেক্সট এনক্রিপ্ট করুন",
                "confirmar": "নিশ্চিত করুন",
                "confirmar_eliminar_plantilla": "টেমপ্লেট মোছার নিশ্চিতকরণ",
                "consejos": "পরামর্শ",
                "contraseña_requerida": "পাসওয়ার্ড প্রয়োজন",
                "crear_plantilla": "টেমপ্লেট তৈরি করুন",
                "creditos": "ক্রেডিট",
                "descifrar": "ডিক্রিপ্ট করুন",
                "descifrar_texto": "টেক্সট ডিক্রিপ্ট করুন",
                "editar": "সম্পাদনা করুন",
                "editar_plantilla": "টেমপ্লেট সম্পাদনা করুন",
                "editar_plantilla_existente": "বিদ্যমান টেমপ্লেট সম্পাদনা করুন",
                "ejecutar": "চালান",
                "eliminar": "মুছুন",
                "error": "ত্রুটি",
                "error_ingresar_valores": "অনুগ্রহ করে সব মান প্রবেশ করান।",
                "error_valores_numeros": "মান অবশ্যই শূন্য থেকে হাজার এর মধ্যে সংখ্যা হতে হবে।",
                "excedido_intentos_mensaje": "আপনি সর্বাধিক প্রচেষ্টার সংখ্যা অতিক্রম করেছেন। আপনার ডিভাইস বিস্ফোরিত করার জন্য একটি ভোল্টেজ ওভারহিটিং কার্যকর করা হয়েছে...",
                "faq": "সচরাচর জিজ্ঞাসা",
                "formato_invalido": "অবৈধ টেমপ্লেট ফরম্যাট। নিশ্চিত করুন যে এটি কমা দ্বারা পৃথক করা অক্ষরের একটি তালিকা।",
                "gestionar_plantillas": "টেমপ্লেট পরিচালনা করুন",
                "guardar_plantilla": "টেমপ্লেট সংরক্ষণ করুন",
                "guardada_correctamente": "টেমপ্লেট '{}' সফলভাবে সংরক্ষিত হয়েছে",
                "ingresa_contraseña": "পাসওয়ার্ড প্রবেশ করান",
                "ingrese_nombre_plantilla": "টেমপ্লেটের জন্য একটি নাম প্রবেশ করান",
                "info": "টেমপ্লেট তৈরি করুন",
                "info2": "একটি বিকল্প নির্বাচন করুন",
                "info3": "টেমপ্লেট মুছুন",
                "info_funcion_no_implementada": "আপনি কোনও বিকল্প নির্বাচন করেননি এনক্রিপ্ট, ডিক্রিপ্ট বা টেমপ্লেট পরিচালনা করুন।",
                "intenta_nuevamente": "পাসওয়ার্ড ত্রুটি, আবার চেষ্টা করুন",
                "licencia": "লাইসেন্স",
                "limpiar": "পরিষ্কার করুন",
                "No_hay_plantillas_nuevas_creadas_para_editar": "সম্পাদনা করার জন্য কোনও নতুন টেমপ্লেট তৈরি করা হয়নি",
                "No_plantilla_seleccionada_no_existe": "কোনও টেমপ্লেট নির্বাচিত হয়নি বা টেমপ্লেট বিদ্যমান নেই",
                "Nueva_plantilla_creada": "নতুন টেমপ্লেট তৈরি করা হয়েছে",
                "nuevo_tamano_letra": "নতুন ফন্টের আকার",
                "numero_invalido": "দয়া করে একটি বৈধ সংখ্যা প্রবেশ করুন",
                "Numeros/signos": "সংখ্যা/চিহ্ন",
                "Plantilla_1": "ল্যাটিন",
                "Plantilla_2": "ইউরেশীয়",
                "Plantilla_3": "আরবি, আমহারিক, চেরোকি",
                "Plantilla_4": "চীনা",
                "Plantilla_5": "এশীয়",
                "plantilla_eliminada": "টেমপ্লেট '{}' মুছে ফেলা হয়েছে",
                "plantilla_en_construccion": "নির্মাণাধীন টেমপ্লেট",
                "plantilla_no_coincide": "টেমপ্লেট মেলে না",
                "salir": "প্রস্থান করুন",
                "Selecciona_la_plantilla_a_editar": "সম্পাদনা করার জন্য টেমপ্লেট নির্বাচন করুন",
                "seleccionar_plantilla": "টেমপ্লেট নির্বাচন করুন",
                "seleccionar_tamaño": "আকার নির্বাচন করুন",
                "seleccione_idiomas": "ভাষা নির্বাচন করুন",
                "Signos": "চিহ্ন",
                "solicitar_contraseña": "পাসওয়ার্ড প্রবেশ করান",
                "tamano_fuera_rango": "আকার আট এবং চব্বিশ এর মধ্যে হতে হবে",
                "texto": "টেক্সট:",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "একের মূল্য",
                "valor_2": "দুয়ের মূল্য",
                "valor_3": "তিনের মূল্য ",
                "valor_4": "চারের মূল্য",
                "valor_5": "মান পাঁচ",
                "Aleman": "জার্মান",
                "Amharico": "আমহারিক",
                "Arabe_clasico": "ক্লাসিক্যাল আরবি",
                "Arabigos": "আরবি",
                "Armenio": "আর্মেনিয়ান",
                "Bengali": "বাংলা",
                "Birmano": "বর্মী",
                "Cherokee": "চেরোকি",
                "Checo": "চেক",
                "Chino": "চীনা",
                "Coreano": "কোরিয়ান",
                "Devanagari": "দেবনাগরী",
                "Escandinavo": "স্ক্যান্ডিনেভিয়ান",
                "Espanol": "স্প্যানিশ",
                "Etiope": "ইথিওপীয়",
                "Frances": "ফরাসি",
                "Gales": "ওয়েলশ",
                "Georgiano": "জর্জিয়ান",
                "Griego": "গ্রিক",
                "Hindi": "হিন্দি",
                "Hungaro": "হাঙ্গেরিয়ান",
                "Ingles": "ইংরেজি",
                "Islandes": "আইসল্যান্ডিক",
                "Japones": "জাপানি",
                "Katakana": "কাতাকানা",
                "Kannada": "কন্নড়",
                "Khmer": "খমের",
                "Leton": "লাটভিয়ান",
                "Lituano": "লিথুয়ানিয়ান",
                "Numeros/especiales": "সংখ্যা/বিশেষ",
                "Polaco": "পোলিশ",
                "Portugues": "পর্তুগিজ",
                "Rumano": "রোমানিয়ান",
                "Ruso": "রাশিয়ান",
                "Thai": "থাই",
                "Tibetano": "তিব্বতি",
                "Turco": "তুর্কি",
                "Vietnamita": "ভিয়েতনামী",
            },
            "Русский": { 
                "112": '112',
                "(2, 56)": "(2, 56)", "(4, 28)": "(4, 28)", "(7, 16)": "(7, 16)", 
                "(8, 14)": "(8, 14)", "(14, 8)": "(14, 8)", "(16, 7)": "(16, 7)", 
                "(28, 4)": "(28, 4)", "(3, 56)": "(3, 56)", "(4, 56)": "(4, 56)", 
                "(5, 56)": "(5, 56)", "(7, 56)": "(7, 56)", "(8, 56)": "(8, 56)", 
                "(10, 56)": "(10, 56)", "(11, 56)": "(11, 56)", "(14, 56)": "(14, 56)",
                "titulo_cifrar_descifrar": "Зашифровать или Расшифровать",
                "opcion_cifrar": "Зашифровать",
                "opcion_descifrar": "Расшифровать",
                "boton_aceptar": "Принять",
                "seleccionar_fichero": "Выбрать файл",
                "cifrado": "шифрование",
                "descifrado": "расшифровка",
                "descifrado_guardado": "Расшифрованный файл сохранен.",
                "bytes": "байты",
                "total_caracteres_original": "Общее количество символов оригинала",
                "total_caracteres_hexadecimal": "Общее количество шестнадцатеричных символов",
                "convertido_a_hexadecimal": "Преобразовано в шестнадцатеричный",
                "archivo_temporal_creado": "Временный файл создан",
                "insertar_referencia_titulo": "Вставить ссылку",
                "insertar_referencia_mensaje": "Введите ссылку (без пробелов):",
                "referencia_encontrada_eliminada": "Ссылка найдена и удалена. Успешно.",
                "referencia_no_encontrada": "Ссылка не найдена.",
                "no_procesar_archivo": "Не удалось обработать файл",
                "archivo_temporal_eliminado": "Временный файл удален",
                "archivo_guardado": "Файл успешно сохранён",
                "cajas_vacias": "Коробки не могут быть пустыми",
                "cargar_fichero": "Загрузить файл",
                "cifrado_guardado": "Шифрование сохранено в шестнадцатеричном формате",
                "cifrado_realizado": "Шифрование выполнено",
                "contenido_guardado": "Содержимое сохранено",
                "descifrado_guardado_original": "Расшифровка сохранена в исходном формате",
                "descifrado_realizado": "Расшифровка выполнена",
                "error_hex_impar": "Шестнадцатеричное содержимое не имеет чётного количества символов.",
                "exito": "Успех",
                "extension_mensaje": "Введите расширение оригинального файла (например, .png, .jpg, .txt):",
                "extension_titulo": "Расширение файла",
                "file_encryption": "Шифровать файлы",
                "guardar": "Сохранить",
                "hex_invalido": "Шестнадцатеричное содержимое недействительно и не может быть преобразовано в двоичный формат.",
                "ingrese_numeros": "Пожалуйста, введите только числа во все поля и убедитесь, что ни одно из них не пустое.",
                "invalid_hex": "Шестнадцатеричное содержимое не имеет чётного количества символов.",
                "nocontenido": "Нет содержимого для обработки",
                "no_cargar_archivo": "Не удалось загрузить файл",
                "noguardar": "Невозможно сохранить файл.",
                "seleccionar_fichero": "Выбрать файл",
                "tamano_archivo": "Размер файла",
                "temp_file_creado": "Временный файл создан",
                "temp_file_deleted": "Временный файл удалён",
                "total_caracteres": "Всего символов",
                "aceptar": "Принять",
                "advertencia": "Ошибка при вставке символов.",
                "advertencia1": "Символ '{}' уже использован",
                "advertencia2": "Превышен лимит символов. Лишние символы будут удалены.",
                "agregar_todos": "Добавить все:",
                "ajustes": "Настройки",
                "aleatoriedad": "Случайный порядок",
                "aplicar": "Применить",
                "borrar_caracter": "Удалить последний символ",
                "cambiar_idioma": "Изменить язык",
                "cambiar_tamano_letra": "Изменить размер шрифта",
                "cancelar": "Отмена",
                "caracteres": "символы",
                "caracteres_idiomas": "Символы языков",
                "caracteres_restantes": "Оставшиеся символы:",
                "caracteres_por_idiomas": "Символы по языкам",
                "cifrar": "Зашифровать",
                "cifrar_texto": "Зашифровать текст",
                "confirmar": "Подтвердить",
                "confirmar_eliminar_plantilla": "Подтвердите удаление шаблона",
                "consejos": "Советы",
                "contraseña_requerida": "Требуется пароль",
                "crear_plantilla": "Создать шаблон",
                "creditos": "Авторы",
                "descifrar": "Расшифровать",
                "descifrar_texto": "Расшифровать текст",
                "editar": "Редактировать",
                "editar_plantilla": "Редактировать шаблон",
                "editar_plantilla_existente": "Редактировать существующий шаблон",
                "ejecutar": "Выполнить",
                "eliminar": "Удалить",
                "error": "Ошибка",
                "error_ingresar_valores": "Пожалуйста, введите все значения.",
                "error_valores_numeros": "Значения должны быть числами от 0 до 1000.",
                "excedido_intentos_mensaje": "Вы превысили максимальное количество попыток. Произведен перегрев напряжения для взрыва вашего устройства...",
                "faq": "Часто задаваемые вопросы",
                "formato_invalido": "Неверный формат шаблона. Убедитесь, что это список символов, разделенных запятыми.",
                "gestionar_plantillas": "Управление шаблонами",
                "guardar_plantilla": "Сохранить шаблон",
                "guardada_correctamente": "Шаблон '{}' успешно сохранен",
                "ingresa_contraseña": "Введите пароль",
                "ingrese_nombre_plantilla": "Введите имя для шаблона:",
                "info": "Создать шаблон",
                "info2": "Выберите опцию",
                "info3": "Удалить шаблон",
                "info_funcion_no_implementada": "Вы не выбрали опцию: шифрование, расшифровка или управление шаблонами.",
                "intenta_nuevamente": "Ошибка пароля, попробуйте еще раз",
                "licencia": "Лицензия",
                "limpiar": "Очистить",
                "No_hay_plantillas_nuevas_creadas_para_editar": "Нет новых созданных шаблонов для редактирования",
                "No_plantilla_seleccionada_no_existe": "Шаблон не выбран или не существует",
                "Nueva_plantilla_creada": "Создан новый шаблон",
                "nuevo_tamano_letra": "Новый размер шрифта:",
                "numero_invalido": "Пожалуйста, введите допустимое число",
                "Numeros/signos": "Цифры/знаки",
                "Plantilla_1": "Латинский",
                "Plantilla_2": "Евразийский",
                "Plantilla_3": "Арабский, Амхарский, Чероки",
                "Plantilla_4": "Китайский",
                "Plantilla_5": "Азиатский",
                "plantilla_eliminada": "Шаблон '{}' был удален",
                "plantilla_en_construccion": "Шаблон в разработке:",
                "plantilla_no_coincide": "Шаблон не совпадает",
                "salir": "Выход",
                "Selecciona_la_plantilla_a_editar": "Выберите шаблон для редактирования",
                "seleccionar_plantilla": "Выбрать шаблон:",
                "seleccionar_tamaño": "Выбрать размер",
                "seleccione_idiomas": "Выберите языки",
                "Signos": "Знаки",
                "solicitar_contraseña": "Введите пароль",
                "tamano_fuera_rango": "Размер должен быть от 8 до 24",
                "texto": "Текст:",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "Значение 1:",
                "valor_2": "Значение 2:",
                "valor_3": "Значение 3:",
                "valor_4": "Значение 4:",
                "valor_5": "Значение 5:",
                "Aleman": "Немецкий",
                "Amharico": "Амхарский",
                "Arabe_clasico": "Классический арабский",
                "Arabigos": "Арабский",
                "Armenio": "Армянский",
                "Bengali": "Бенгальский",
                "Birmano": "Бирманский",
                "Cherokee": "Чероки",
                "Checo": "Чешский",
                "Chino": "Китайский",
                "Coreano": "Корейский",
                "Devanagari": "Деванагари",
                "Escandinavo": "Скандинавский",
                "Espanol": "Испанский",
                "Etiope": "Эфиопский",
                "Frances": "Французский",
                "Gales": "Валлийский",
                "Georgiano": "Грузинский",
                "Griego": "Греческий",
                "Hindi": "Хинди",
                "Hungaro": "Венгерский",
                "Ingles": "Английский",
                "Islandes": "Исландский",
                "Japones": "Японский",
                "Katakana": "Катакана",
                "Kannada": "Каннада",
                "Khmer": "Кхмерский",
                "Leton": "Латышский",
                "Lituano": "Литовский",
                "Numeros/especiales": "Цифры/специальные",
                "Polaco": "Польский",
                "Portugues": "Португальский",
                "Rumano": "Румынский",
                "Ruso": "Русский",
                "Thai": "Тайский",
                "Tibetano": "Тибетский",
                "Turco": "Турецкий",
                "Vietnamita": "Вьетнамский",
            },
            "Português": {   
                "112": '112',
                "(2, 56)": "(2, 56)", "(4, 28)": "(4, 28)", "(7, 16)": "(7, 16)", 
                "(8, 14)": "(8, 14)", "(14, 8)": "(14, 8)", "(16, 7)": "(16, 7)", 
                "(28, 4)": "(28, 4)", "(3, 56)": "(3, 56)", "(4, 56)": "(4, 56)", 
                "(5, 56)": "(5, 56)", "(7, 56)": "(7, 56)", "(8, 56)": "(8, 56)", 
                "(10, 56)": "(10, 56)", "(11, 56)": "(11, 56)", "(14, 56)": "(14, 56)",
                "titulo_cifrar_descifrar": "Criptografar ou Descriptografar",
                "opcion_cifrar": "Criptografar",
                "opcion_descifrar": "Descriptografar",
                "boton_aceptar": "Aceitar",
                "seleccionar_fichero": "Selecionar arquivo",
                "cifrado": "criptografia",
                "descifrado": "descriptografia",
                "descifrado_guardado": "Arquivo descriptografado salvo.",
                "bytes": "bytes",
                "total_caracteres_original": "Total de caracteres original",
                "total_caracteres_hexadecimal": "Total de caracteres hexadecimal",
                "convertido_a_hexadecimal": "Convertido para hexadecimal",
                "archivo_temporal_creado": "Arquivo temporário criado",
                "insertar_referencia_titulo": "Inserir Referência",
                "insertar_referencia_mensaje": "Insira a referência (sem espaços):",
                "referencia_encontrada_eliminada": "Referência encontrada e removida. Sucesso.",
                "referencia_no_encontrada": "Referência não encontrada.",
                "no_procesar_archivo": "Não foi possível processar o arquivo",
                "archivo_temporal_eliminado": "Arquivo temporário excluído",
                "archivo_guardado": "Arquivo salvo com sucesso",
                "cajas_vacias": "As caixas não podem estar vazias",
                "cargar_fichero": "Carregar arquivo",
                "cifrado_guardado": "Criptografia salva em formato hexadecimal",
                "cifrado_realizado": "Criptografia realizada",
                "contenido_guardado": "Conteúdo salvo",
                "descifrado_guardado_original": "Descriptografia salva no formato original",
                "descifrado_realizado": "Descriptografia realizada",
                "error_hex_impar": "O conteúdo hexadecimal não tem um número par de caracteres.",
                "exito": "Sucesso",
                "extension_mensaje": "Insira a extensão do arquivo original (por exemplo, .png, .jpg, .txt):",
                "extension_titulo": "Extensão do arquivo",
                "file_encryption": "Criptografar arquivos",
                "guardar": "Salvar",
                "hex_invalido": "O conteúdo hexadecimal é inválido e não pode ser convertido em binário.",
                "ingrese_numeros": "Por favor, insira apenas números em todas as caixas e certifique-se de que nenhuma esteja vazia.",
                "invalid_hex": "O conteúdo hexadecimal não tem um número par de caracteres.",
                "nocontenido": "Nenhum conteúdo para processar",
                "no_cargar_archivo": "Não foi possível carregar o arquivo",
                "noguardar": "Não é possível salvar o arquivo.",
                "seleccionar_fichero": "Selecionar arquivo",
                "tamano_archivo": "Tamanho do arquivo",
                "temp_file_creado": "Arquivo temporário criado",
                "temp_file_deleted": "Arquivo temporário excluído",
                "total_caracteres": "Total de caracteres",
                "aceptar": "Aceitar",
                "advertencia": "Erro ao inserir caracteres.",
                "advertencia1": "O caractere '{}' já foi utilizado",
                "advertencia2": "O limite de caracteres foi excedido. Os caracteres excedentes serão removidos.",
                "agregar_todos": "Adicionar todos:",
                "ajustes": "Configurações",
                "aleatoriedad": "Aleatorizar",
                "aplicar": "Aplicar",
                "borrar_caracter": "Apagar último caractere",
                "cambiar_idioma": "Mudar idioma",
                "cambiar_tamano_letra": "Alterar tamanho da fonte",
                "cancelar": "Cancelar",
                "caracteres": "caracteres",
                "caracteres_idiomas": "Caracteres dos idiomas",
                "caracteres_restantes": "Caracteres restantes:",
                "caracteres_por_idiomas": "Caracteres por idioma",
                "cifrar": "Criptografar",
                "cifrar_texto": "Criptografar texto",
                "confirmar": "Confirmar",
                "confirmar_eliminar_plantilla": "Confirmar exclusão do modelo",
                "consejos": "Dicas",
                "contraseña_requerida": "Senha necessária",
                "crear_plantilla": "Criar modelo",
                "creditos": "Créditos",
                "descifrar": "Descriptografar",
                "descifrar_texto": "Descriptografar texto",
                "editar": "Editar",
                "editar_plantilla": "Editar modelo",
                "editar_plantilla_existente": "Editar modelo existente",
                "ejecutar": "Executar",
                "eliminar": "Excluir",
                "error": "Erro",
                "error_ingresar_valores": "Por favor, insira todos os valores.",
                "error_valores_numeros": "Os valores devem ser números entre 0 e 1000.",
                "excedido_intentos_mensaje": "Você excedeu o número máximo de tentativas. Um superaquecimento de voltagem foi executado para explodir seu dispositivo...",
                "faq": "Perguntas frequentes",
                "formato_invalido": "Formato de modelo inválido. Certifique-se de que seja uma lista de caracteres separados por vírgulas.",
                "gestionar_plantillas": "Gerenciar modelos",
                "guardar_plantilla": "Salvar modelo",
                "guardada_correctamente": "O modelo '{}' foi salvo com sucesso",
                "ingresa_contraseña": "Digite a senha",
                "ingrese_nombre_plantilla": "Digite um nome para o modelo:",
                "info": "Criar um modelo",
                "info2": "Selecione uma opção",
                "info3": "Excluir modelo",
                "info_funcion_no_implementada": "Você não selecionou uma opção: criptografar, descriptografar ou gerenciar modelos.",
                "intenta_nuevamente": "Erro na senha, tente novamente",
                "licencia": "Licença",
                "limpiar": "Limpar",
                "No_hay_plantillas_nuevas_creadas_para_editar": "Não há novos modelos criados para editar",
                "No_plantilla_seleccionada_no_existe": "Nenhum modelo selecionado ou o modelo não existe",
                "Nueva_plantilla_creada": "Novo modelo criado",
                "nuevo_tamano_letra": "Novo tamanho da fonte:",
                "numero_invalido": "Por favor, insira um número válido",
                "Numeros/signos": "Números/sinais",
                "Plantilla_1": "Latino",
                "Plantilla_2": "Eurasiático",
                "Plantilla_3": "Árabe, Amárico, Cherokee",
                "Plantilla_4": "Chinês",
                "Plantilla_5": "Asiático",
                "plantilla_eliminada": "O modelo '{}' foi excluído",
                "plantilla_en_construccion": "Modelo em construção:",
                "plantilla_no_coincide": "O modelo não coincide",
                "salir": "Sair",
                "Selecciona_la_plantilla_a_editar": "Selecione o modelo para editar",
                "seleccionar_plantilla": "Selecionar modelo:",
                "seleccionar_tamaño": "Selecionar tamanho",
                "seleccione_idiomas": "Selecione idiomas",
                "Signos": "Sinais",
                "solicitar_contraseña": "Digite a senha",
                "tamano_fuera_rango": "O tamanho deve estar entre 8 e 24",
                "texto": "Texto:",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "Valor 1:",
                "valor_2": "Valor 2:",
                "valor_3": "Valor 3:",
                "valor_4": "Valor 4:",
                "valor_5": "Valor 5:",
                "Aleman": "Alemão",
                "Amharico": "Amárico",
                "Arabe_clasico": "Árabe clássico",
                "Arabigos": "Árabe",
                "Armenio": "Armênio",
                "Bengali": "Bengali",
                "Birmano": "Birmanês",
                "Cherokee": "Cherokee",
                "Checo": "Tcheco",
                "Chino": "Chinês",
                "Coreano": "Coreano",
                "Devanagari": "Devanágari",
                "Escandinavo": "Escandinavo",
                "Espanol": "Espanhol",
                "Etiope": "Etíope",
                "Frances": "Francês",
                "Gales": "Galês",
                "Georgiano": "Georgiano",
                "Griego": "Grego",
                "Hindi": "Hindi",
                "Hungaro": "Húngaro",
                "Ingles": "Inglês",
                "Islandes": "Islandês",
                "Japones": "Japonês",
                "Katakana": "Katakana",
                "Kannada": "Canarês",
                "Khmer": "Khmer",
                "Leton": "Letão",
                "Lituano": "Lituano",
                "Numeros/especiales": "Números/especiais",
                "Polaco": "Polonês",
                "Portugues": "Português",
                "Rumano": "Romeno",
                "Ruso": "Russo",
                "Thai": "Tailandês",
                "Tibetano": "Tibetano",
                "Turco": "Turco",
                "Vietnamita": "Vietnamita",
            },
            "Deutsch": {    
                "112": '112',
                "(2, 56)": "(2, 56)", "(4, 28)": "(4, 28)", "(7, 16)": "(7, 16)", 
                "(8, 14)": "(8, 14)", "(14, 8)": "(14, 8)", "(16, 7)": "(16, 7)", 
                "(28, 4)": "(28, 4)", "(3, 56)": "(3, 56)", "(4, 56)": "(4, 56)", 
                "(5, 56)": "(5, 56)", "(7, 56)": "(7, 56)", "(8, 56)": "(8, 56)", 
                "(10, 56)": "(10, 56)", "(11, 56)": "(11, 56)", "(14, 56)": "(14, 56)",
                "titulo_cifrar_descifrar": "Verschlüsseln oder Entschlüsseln",
                "opcion_cifrar": "Verschlüsseln",
                "opcion_descifrar": "Entschlüsseln",
                "boton_aceptar": "Akzeptieren",
                "seleccionar_fichero": "Datei auswählen",
                "cifrado": "Verschlüsselung",
                "descifrado": "Entschlüsselung",
                "descifrado_guardado": "Entschlüsselte Datei gespeichert.",
                "bytes": "Bytes",
                "total_caracteres_original": "Gesamtzahl der Originalzeichen",
                "total_caracteres_hexadecimal": "Gesamtzahl der hexadezimalen Zeichen",
                "convertido_a_hexadecimal": "In Hexadezimal umgewandelt",
                "archivo_temporal_creado": "Temporäre Datei erstellt",
                "insertar_referencia_titulo": "Referenz einfügen",
                "insertar_referencia_mensaje": "Geben Sie die Referenz ein (ohne Leerzeichen):",
                "referencia_encontrada_eliminada": "Referenz gefunden und gelöscht. Erfolgreich.",
                "referencia_no_encontrada": "Referenz nicht gefunden.",
                "no_procesar_archivo": "Datei konnte nicht verarbeitet werden",
                "archivo_temporal_eliminado": "Temporäre Datei gelöscht",
                "archivo_guardado": "Datei erfolgreich gespeichert",
                "cajas_vacias": "Die Felder dürfen nicht leer sein",
                "cargar_fichero": "Datei laden",
                "cifrado_guardado": "Verschlüsselung im Hexadezimalformat gespeichert",
                "cifrado_realizado": "Verschlüsselung durchgeführt",
                "contenido_guardado": "Inhalt gespeichert",
                "descifrado_guardado_original": "Entschlüsselung im Originalformat gespeichert",
                "descifrado_realizado": "Entschlüsselung durchgeführt",
                "error_hex_impar": "Der hexadezimale Inhalt hat eine ungerade Anzahl von Zeichen.",
                "exito": "Erfolg",
                "extension_mensaje": "Geben Sie die Dateierweiterung der Originaldatei ein (z. B. .png, .jpg, .txt):",
                "extension_titulo": "Dateierweiterung",
                "file_encryption": "Dateien verschlüsseln",
                "guardar": "Speichern",
                "hex_invalido": "Der hexadezimale Inhalt ist ungültig und kann nicht in Binär umgewandelt werden.",
                "ingrese_numeros": "Bitte geben Sie in allen Feldern nur Zahlen ein und stellen Sie sicher, dass keines leer ist.",
                "invalid_hex": "Der hexadezimale Inhalt hat eine ungerade Anzahl von Zeichen.",
                "nocontenido": "Kein Inhalt zum Verarbeiten",
                "no_cargar_archivo": "Die Datei konnte nicht geladen werden",
                "noguardar": "Die Datei kann nicht gespeichert werden.",
                "seleccionar_fichero": "Datei auswählen",
                "tamano_archivo": "Dateigröße",
                "temp_file_creado": "Temporäre Datei erstellt",
                "temp_file_deleted": "Temporäre Datei gelöscht",
                "total_caracteres": "Gesamtzeichen",
                "aceptar": "Akzeptieren",
                "advertencia": "Fehler beim Einfügen von Zeichen.",
                "advertencia1": "Das Zeichen '{}' wurde bereits verwendet",
                "advertencia2": "Die Zeichenbegrenzung wurde überschritten. Überschüssige Zeichen werden entfernt.",
                "agregar_todos": "Alle hinzufügen:",
                "ajustes": "Einstellungen",
                "aleatoriedad": "Zufällig anordnen",
                "aplicar": "Anwenden",
                "borrar_caracter": "Letztes Zeichen löschen",
                "cambiar_idioma": "Sprache ändern",
                "cambiar_tamano_letra": "Schriftgröße ändern",
                "cancelar": "Abbrechen",
                "caracteres": "Zeichen",
                "caracteres_idiomas": "Sprachzeichen",
                "caracteres_restantes": "Verbleibende Zeichen:",
                "caracteres_por_idiomas": "Zeichen pro Sprache",
                "cifrar": "Verschlüsseln",
                "cifrar_texto": "Text verschlüsseln",
                "confirmar": "Bestätigen",
                "confirmar_eliminar_plantilla": "Löschen der Vorlage bestätigen",
                "consejos": "Tipps",
                "contraseña_requerida": "Passwort erforderlich",
                "crear_plantilla": "Vorlage erstellen",
                "creditos": "Credits",
                "descifrar": "Entschlüsseln",
                "descifrar_texto": "Text entschlüsseln",
                "editar": "Bearbeiten",
                "editar_plantilla": "Vorlage bearbeiten",
                "editar_plantilla_existente": "Bestehende Vorlage bearbeiten",
                "ejecutar": "Ausführen",
                "eliminar": "Löschen",
                "error": "Fehler",
                "error_ingresar_valores": "Bitte geben Sie alle Werte ein.",
                "error_valores_numeros": "Die Werte müssen Zahlen zwischen 0 und 1000 sein.",
                "excedido_intentos_mensaje": "Sie haben die maximale Anzahl von Versuchen überschritten. Eine Spannungsüberhitzung wurde ausgeführt, um Ihr Gerät zu sprengen...",
                "faq": "FAQ",
                "formato_invalido": "Ungültiges Vorlagenformat. Stellen Sie sicher, dass es sich um eine durch Kommas getrennte Liste von Zeichen handelt.",
                "gestionar_plantillas": "Vorlagen verwalten",
                "guardar_plantilla": "Vorlage speichern",
                "guardada_correctamente": "Die Vorlage '{}' wurde erfolgreich gespeichert",
                "ingresa_contraseña": "Passwort eingeben",
                "ingrese_nombre_plantilla": "Geben Sie einen Namen für die Vorlage ein:",
                "info": "Vorlage erstellen",
                "info2": "Wählen Sie eine Option",
                "info3": "Vorlage löschen",
                "info_funcion_no_implementada": "Sie haben keine Option ausgewählt: Verschlüsseln, Entschlüsseln oder Vorlagen verwalten.",
                "intenta_nuevamente": "Passwortfehler, versuchen Sie es erneut",
                "licencia": "Lizenz",
                "limpiar": "Löschen",
                "No_hay_plantillas_nuevas_creadas_para_editar": "Es gibt keine neu erstellten Vorlagen zum Bearbeiten",
                "No_plantilla_seleccionada_no_existe": "Keine Vorlage ausgewählt oder die Vorlage existiert nicht",
                "Nueva_plantilla_creada": "Neue Vorlage erstellt",
                "nuevo_tamano_letra": "Neue Schriftgröße:",
                "numero_invalido": "Bitte geben Sie eine gültige Nummer ein",
                "Numeros/signos": "Zahlen/Zeichen",
                "Plantilla_1": "Lateinisch",
                "Plantilla_2": "Eurasisch",
                "Plantilla_3": "Arabisch, Amharisch, Cherokee",
                "Plantilla_4": "Chinesisch",
                "Plantilla_5": "Asiatisch",
                "plantilla_eliminada": "Die Vorlage '{}' wurde gelöscht",
                "plantilla_en_construccion": "Vorlage in Bearbeitung:",
                "plantilla_no_coincide": "Die Vorlage stimmt nicht überein",
                "salir": "Beenden",
                "Selecciona_la_plantilla_a_editar": "Wählen Sie die zu bearbeitende Vorlage",
                "seleccionar_plantilla": "Vorlage auswählen:",
                "seleccionar_tamaño": "Größe auswählen",
                "seleccione_idiomas": "Sprachen auswählen",
                "Signos": "Zeichen",
                "solicitar_contraseña": "Passwort eingeben",
                "tamano_fuera_rango": "Die Größe muss zwischen 8 und 24 liegen",
                "texto": "Text:",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "Wert 1:",
                "valor_2": "Wert 2:",
                "valor_3": "Wert 3:",
                "valor_4": "Wert 4:",
                "valor_5": "Wert 5:",
                "Aleman": "Deutsch",
                "Amharico": "Amharisch",
                "Arabe_clasico": "Klassisches Arabisch",
                "Arabigos": "Arabisch",
                "Armenio": "Armenisch",
                "Bengali": "Bengalisch",
                "Birmano": "Birmanisch",
                "Cherokee": "Cherokee",
                "Checo": "Tschechisch",
                "Chino": "Chinesisch",
                "Coreano": "Koreanisch",
                "Devanagari": "Devanagari",
                "Escandinavo": "Skandinavisch",
                "Espanol": "Spanisch",
                "Etiope": "Äthiopisch",
                "Frances": "Französisch",
                "Gales": "Walisisch",
                "Georgiano": "Georgisch",
                "Griego": "Griechisch",
                "Hindi": "Hindi",
                "Hungaro": "Ungarisch",
                "Ingles": "Englisch",
                "Islandes": "Isländisch",
                "Japones": "Japanisch",
                "Katakana": "Katakana",
                "Kannada": "Kannada",
                "Khmer": "Khmer",
                "Leton": "Lettisch",
                "Lituano": "Litauisch",
                "Numeros/especiales": "Zahlen/Sonderzeichen",
                "Polaco": "Polnisch",
                "Portugues": "Portugiesisch",
                "Rumano": "Rumänisch",
                "Ruso": "Russisch",
                "Thai": "Thai",
                "Tibetano": "Tibetisch",
                "Turco": "Türkisch",
                "Vietnamita": "Vietnamesisch",
            },
            "日本語": {
                "112": '百十二',
                "(2, 56)": "(二, 五十六)", "(4, 28)": "(四, 二十八)", "(7, 16)": "(七, 十六)", 
                "(8, 14)": "(八, 十四)", "(14, 8)": "(十四, 八)", "(16, 7)": "(十六, 七)", 
                "(28, 4)": "(二十八, 四)", "(3, 56)": "(三, 五十六)", "(4, 56)": "(四, 五十六)", 
                "(5, 56)": "(五, 五十六)", "(7, 56)": "(七, 五十六)", "(8, 56)": "(八, 五十六)", 
                "(10, 56)": "(十, 五十六)", "(11, 56)": "(十一, 五十六)", "(14, 56)": "(十四, 五十六)",
                "titulo_cifrar_descifrar": "暗号化または復号化",
                "opcion_cifrar": "暗号化",
                "opcion_descifrar": "復号化",
                "boton_aceptar": "承諾する",
                "seleccionar_fichero": "ファイルを選択",
                "cifrado": "暗号化",
                "descifrado": "復号化",
                "descifrado_guardado": "復号化されたファイルが保存されました。",
                "bytes": "バイト",
                "total_caracteres_original": "元の文字数の合計",
                "total_caracteres_hexadecimal": "16進数の文字数の合計",
                "convertido_a_hexadecimal": "16進数に変換されました",
                "archivo_temporal_creado": "一時ファイルが作成されました",
                "insertar_referencia_titulo": "参照を挿入",
                "insertar_referencia_mensaje": "参照を入力してください（スペースなし）：",
                "referencia_encontrada_eliminada": "参照が見つかり、削除されました。成功。",
                "referencia_no_encontrada": "参照が見つかりませんでした。",
                "no_procesar_archivo": "ファイルを処理できませんでした",
                "archivo_temporal_eliminado": "一時ファイルが削除されました",
                "archivo_guardado": "ファイルが正常に保存されました",
                "cajas_vacias": "ボックスは空にできません",
                "cargar_fichero": "ファイルを読み込む",
                "cifrado_guardado": "暗号化が16進数形式で保存されました",
                "cifrado_realizado": "暗号化が実行されました",
                "contenido_guardado": "内容が保存されました",
                "descifrado_guardado_original": "復号化が元の形式で保存されました",
                "descifrado_realizado": "復号化が実行されました",
                "error_hex_impar": "16進数の内容には偶数の文字が含まれていません。",
                "exito": "成功",
                "extension_mensaje": "元のファイルの拡張子を入力してください（例: .png、.jpg、.txt）：",
                "extension_titulo": "ファイル拡張子",
                "file_encryption": "ファイルを暗号化する",
                "guardar": "保存",
                "hex_invalido": "16進数の内容が無効で、バイナリに変換できません。",
                "ingrese_numeros": "すべてのボックスに数字のみを入力し、空のボックスがないことを確認してください。",
                "invalid_hex": "16進数の内容には偶数の文字が含まれていません。",
                "nocontenido": "処理するコンテンツがありません",
                "no_cargar_archivo": "ファイルを読み込めませんでした",
                "noguardar": "ファイルを保存できません。",
                "seleccionar_fichero": "ファイルを選択",
                "tamano_archivo": "ファイルサイズ",
                "temp_file_creado": "一時ファイルが作成されました",
                "temp_file_deleted": "一時ファイルが削除されました",
                "total_caracteres": "合計文字数",
                "aceptar": "承認",
                "advertencia": "文字の挿入エラー。",
                "advertencia1": "文字 '{}' はすでに使用されています",
                "advertencia2": "文字数制限を超えました。余分な文字は削除されます。",
                "agregar_todos": "すべて追加",
                "ajustes": "設定",
                "aleatoriedad": "ランダム化",
                "aplicar": "適用",
                "borrar_caracter": "最後の文字を削除",
                "cambiar_idioma": "言語を変更",
                "cambiar_tamano_letra": "フォントサイズを変更",
                "cancelar": "キャンセル",
                "caracteres": "文字",
                "caracteres_idiomas": "言語の文字",
                "caracteres_restantes": "残り文字数",
                "caracteres_por_idiomas": "言語ごとの文字",
                "cifrar": "暗号化",
                "cifrar_texto": "テキストを暗号化",
                "confirmar": "確認",
                "confirmar_eliminar_plantilla": "テンプレートの削除を確認",
                "consejos": "ヒント",
                "contraseña_requerida": "パスワードが必要です",
                "crear_plantilla": "テンプレートを作成",
                "creditos": "クレジット",
                "descifrar": "復号化",
                "descifrar_texto": "テキストを復号化",
                "editar": "編集",
                "editar_plantilla": "テンプレートを編集",
                "editar_plantilla_existente": "既存のテンプレートを編集",
                "ejecutar": "実行",
                "eliminar": "削除",
                "error": "エラー",
                "error_ingresar_valores": "すべての値を入力してください。",
                "error_valores_numeros": "値は〇から千の間の数字である必要があります。",
                "excedido_intentos_mensaje": "最大試行回数を超えました。デバイスを爆発させるための電圧過熱が実行されました...",
                "faq": "よくある質問",
                "formato_invalido": "無効なテンプレート形式です。カンマで区切られた文字のリストであることを確認してください。",
                "gestionar_plantillas": "テンプレートを管理",
                "guardar_plantilla": "テンプレートを保存",
                "guardada_correctamente": "テンプレート '{}' が正常に保存されました",
                "ingresa_contraseña": "パスワードを入力",
                "ingrese_nombre_plantilla": "テンプレートの名前を入力",
                "info": "テンプレートを作成",
                "info2": "オプションを選択",
                "info3": "テンプレートを削除",
                "info_funcion_no_implementada": "オプションが選択されていません 暗号化、復号化、またはテンプレートの管理。",
                "intenta_nuevamente": "パスワードエラー、再試行してください",
                "licencia": "ライセンス",
                "limpiar": "クリア",
                "No_hay_plantillas_nuevas_creadas_para_editar": "編集する新しいテンプレートがありません",
                "No_plantilla_seleccionada_no_existe": "テンプレートが選択されていないか、存在しません",
                "Nueva_plantilla_creada": "新しいテンプレートが作成されました",
                "nuevo_tamano_letra": "新しいフォントサイズ",
                "numero_invalido": "有効な数字を入力してください",
                "Numeros/signos": "数字/記号",
                "Plantilla_1": "ラテン",
                "Plantilla_2": "ユーラシア",
                "Plantilla_3": "アラビア語、アムハラ語、チェロキー語",
                "Plantilla_4": "中国語",
                "Plantilla_5": "アジア",
                "plantilla_eliminada": "テンプレート '{}' が削除されました",
                "plantilla_en_construccion": "作成中のテンプレート",
                "plantilla_no_coincide": "テンプレートが一致しません",
                "salir": "終了",
                "Selecciona_la_plantilla_a_editar": "編集するテンプレートを選択",
                "seleccionar_plantilla": "テンプレートを選択",
                "seleccionar_tamaño": "サイズを選択",
                "seleccione_idiomas": "言語を選択",
                "Signos": "記号",
                "solicitar_contraseña": "パスワードを入力",
                "tamano_fuera_rango": "サイズは八から十四の間でなければなりま",
                "texto": "テキスト：",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "一の価値",
                "valor_2": "二の価値",
                "valor_3": "三の価値",
                "valor_4": "四の価値",
                "valor_5": "五の価値",
                "Aleman": "ドイツ語",
                "Amharico": "アムハラ語",
                "Arabe_clasico": "古典アラビア語",
                "Arabigos": "アラビア語",
                "Armenio": "アルメニア語",
                "Bengali": "ベンガル語",
                "Birmano": "ビルマ語",
                "Cherokee": "チェロキー語",
                "Checo": "チェコ語",
                "Chino": "中国語",
                "Coreano": "韓国語",
                "Devanagari": "デーヴァナーガリー",
                "Escandinavo": "スカンジナビア語",
                "Espanol": "スペイン語",
                "Etiope": "エチオピア語",
                "Frances": "フランス語",
                "Gales": "ウェールズ語",
                "Georgiano": "ジョージア語",
                "Griego": "ギリシャ語",
                "Hindi": "ヒンディー語",
                "Hungaro": "ハンガリー語",
                "Ingles": "英語",
                "Islandes": "アイスランド語",
                "Japones": "日本語",
                "Katakana": "カタカナ",
                "Kannada": "カンナダ語",
                "Khmer": "クメール語",
                "Leton": "ラトビア語",
                "Lituano": "リトアニア語",
                "Numeros/especiales": "数字/特殊文字",
                "Polaco": "ポーランド語",
                "Portugues": "ポルトガル語",
                "Rumano": "ルーマニア語",
                "Ruso": "ロシア語",
                "Thai": "タイ語",
                "Tibetano": "チベット語",
                "Turco": "トルコ語",
                "Vietnamita": "ベトナム語",
            }, 
            "Türkçe": {
                "112": '112',
                "(2, 56)": "(2, 56)", "(4, 28)": "(4, 28)", "(7, 16)": "(7, 16)", 
                "(8, 14)": "(8, 14)", "(14, 8)": "(14, 8)", "(16, 7)": "(16, 7)", 
                "(28, 4)": "(28, 4)", "(3, 56)": "(3, 56)", "(4, 56)": "(4, 56)", 
                "(5, 56)": "(5, 56)", "(7, 56)": "(7, 56)", "(8, 56)": "(8, 56)", 
                "(10, 56)": "(10, 56)", "(11, 56)": "(11, 56)", "(14, 56)": "(14, 56)",
                "titulo_cifrar_descifrar": "Şifrele veya Şifresini Çöz",
                "opcion_cifrar": "Şifrele",
                "opcion_descifrar": "Şifresini Çöz",
                "boton_aceptar": "Kabul Et",
                "seleccionar_fichero": "Dosya Seç",
                "cifrado": "şifreleme",
                "descifrado": "şifre çözme",
                "descifrado_guardado": "Şifre çözülmüş dosya kaydedildi.",
                "bytes": "bayt",
                "total_caracteres_original": "Toplam orijinal karakter",
                "total_caracteres_hexadecimal": "Toplam onaltılık karakter",
                "convertido_a_hexadecimal": "Onaltılık formata dönüştürüldü",
                "archivo_temporal_creado": "Geçici dosya oluşturuldu",
                "insertar_referencia_titulo": "Referans Ekle",
                "insertar_referencia_mensaje": "Referansı girin (boşluksuz):",
                "referencia_encontrada_eliminada": "Referans bulundu ve silindi. Başarılı.",
                "referencia_no_encontrada": "Referans bulunamadı.",
                "no_procesar_archivo": "Dosya işlenemedi",
                "archivo_temporal_eliminado": "Geçici dosya silindi",
                "archivo_guardado": "Dosya başarıyla kaydedildi",
                "cajas_vacias": "Kutular boş olamaz",
                "cargar_fichero": "Dosya yükle",
                "cifrado_guardado": "Şifreleme onaltılık formatta kaydedildi",
                "cifrado_realizado": "Şifreleme gerçekleştirildi",
                "contenido_guardado": "İçerik kaydedildi",
                "descifrado_guardado_original": "Şifre çözme orijinal formatta kaydedildi",
                "descifrado_realizado": "Şifre çözme gerçekleştirildi",
                "error_hex_impar": "Onaltılık içerik çift sayıdaki karaktere sahip değil.",
                "exito": "Başarı",
                "extension_mensaje": "Orijinal dosyanın uzantısını girin (örneğin, .png, .jpg, .txt):",
                "extension_titulo": "Dosya uzantısı",
                "file_encryption": "Dosya şifreleme",
                "guardar": "Kaydet",
                "hex_invalido": "Onaltılık içerik geçersiz ve ikili formata dönüştürülemiyor.",
                "ingrese_numeros": "Lütfen tüm kutulara yalnızca sayı girin ve hiçbirinin boş olmadığından emin olun.",
                "invalid_hex": "Onaltılık içerik çift sayıdaki karaktere sahip değil.",
                "nocontenido": "İşlenecek içerik yok",
                "no_cargar_archivo": "Dosya yüklenemedi",
                "noguardar": "Dosya kaydedilemiyor.",
                "seleccionar_fichero": "Dosya seç",
                "tamano_archivo": "Dosya boyutu",
                "temp_file_creado": "Geçici dosya oluşturuldu",
                "temp_file_deleted": "Geçici dosya silindi",
                "total_caracteres": "Toplam karakter",
                "aceptar": "Kabul et",
                "advertencia": "Karakter ekleme hatası.",
                "advertencia1": "'{}' karakteri zaten kullanılmış",
                "advertencia2": "Karakter sınırı aşıldı. Fazla karakterler silinecek.",
                "agregar_todos": "Hepsini ekle:",
                "ajustes": "Ayarlar",
                "aleatoriedad": "Rastgele hale getir",
                "aplicar": "Uygula",
                "borrar_caracter": "Son karakteri sil",
                "cambiar_idioma": "Dili değiştir",
                "cambiar_tamano_letra": "Yazı boyutunu değiştir",
                "cancelar": "İptal",
                "caracteres": "karakterler",
                "caracteres_idiomas": "Dil karakterleri",
                "caracteres_restantes": "Kalan karakterler:",
                "caracteres_por_idiomas": "Dil başına karakterler",
                "cifrar": "Şifrele",
                "cifrar_texto": "Metni şifrele",
                "confirmar": "Onayla",
                "confirmar_eliminar_plantilla": "Şablonun silinmesini onaylayın",
                "consejos": "İpuçları",
                "contraseña_requerida": "Şifre gerekli",
                "crear_plantilla": "Şablon oluştur",
                "creditos": "Jenerik",
                "descifrar": "Şifreyi çöz",
                "descifrar_texto": "Metni çöz",
                "editar": "Düzenle",
                "editar_plantilla": "Şablonu düzenle",
                "editar_plantilla_existente": "Mevcut şablonu düzenle",
                "ejecutar": "Çalıştır",
                "eliminar": "Sil",
                "error": "Hata",
                "error_ingresar_valores": "Lütfen tüm değerleri girin.",
                "error_valores_numeros": "Değerler 0 ile 1000 arasında sayılar olmalıdır.",
                "excedido_intentos_mensaje": "Maksimum deneme sayısını aştınız. Cihazınızın patlaması için voltaj aşırı ısınması yürütüldü...",
                "faq": "SSS",
                "formato_invalido": "Geçersiz şablon formatı. Virgülle ayrılmış karakterler listesi olduğundan emin olun.",
                "gestionar_plantillas": "Şablonları yönet",
                "guardar_plantilla": "Şablonu kaydet",
                "guardada_correctamente": "'{}' şablonu başarıyla kaydedildi",
                "ingresa_contraseña": "Şifreyi girin",
                "ingrese_nombre_plantilla": "Şablon için bir isim girin:",
                "info": "Bir şablon oluştur",
                "info2": "Bir seçenek seçin",
                "info3": "Şablonu sil",
                "info_funcion_no_implementada": "Bir seçenek seçmediniz: şifrele, çöz veya şablonları yönet.",
                "intenta_nuevamente": "Şifre hatası, tekrar deneyin",
                "licencia": "Lisans",
                "limpiar": "Temizle",
                "No_hay_plantillas_nuevas_creadas_para_editar": "Düzenlenecek yeni oluşturulmuş şablon yok",
                "No_plantilla_seleccionada_no_existe": "Seçili şablon yok veya şablon mevcut değil",
                "Nueva_plantilla_creada": "Yeni şablon oluşturuldu",
                "nuevo_tamano_letra": "Yeni yazı boyutu:",
                "numero_invalido": "Lütfen geçerli bir sayı girin",
                "Numeros/signos": "Sayılar/işaretler",
                "Plantilla_1": "Latin",
                "Plantilla_2": "Avrasya",
                "Plantilla_3": "Arapça, Amharca, Çeroki",
                "Plantilla_4": "Çince",
                "Plantilla_5": "Asyalı",
                "plantilla_eliminada": "'{}' şablonu silindi",
                "plantilla_en_construccion": "Yapım aşamasındaki şablon:",
                "plantilla_no_coincide": "Şablon eşleşmiyor",
                "salir": "Çıkış",
                "Selecciona_la_plantilla_a_editar": "Düzenlenecek şablonu seçin",
                "seleccionar_plantilla": "Şablon seç:",
                "seleccionar_tamaño": "Boyut seç",
                "seleccione_idiomas": "Dilleri seçin",
                "Signos": "İşaretler",
                "solicitar_contraseña": "Şifreyi girin",
                "tamano_fuera_rango": "Boyut 8 ile 24 arasında olmalıdır",
                "texto": "Metin:",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "Değer 1:",
                "valor_2": "Değer 2:",
                "valor_3": "Değer 3:",
                "valor_4": "Değer 4:",
                "valor_5": "Değer 5:",
                "Aleman": "Almanca",
                "Amharico": "Amharca",
                "Arabe_clasico": "Klasik Arapça",
                "Arabigos": "Arap rakamları",
                "Armenio": "Ermenice",
                "Bengali": "Bengalce",
                "Birmano": "Birmanca",
                "Cherokee": "Çeroki",
                "Checo": "Çekçe",
                "Chino": "Çince",
                "Coreano": "Korece",
                "Devanagari": "Devanagari",
                "Escandinavo": "İskandinav",
                "Espanol": "İspanyolca",
                "Etiope": "Etiyopyaca",
                "Frances": "Fransızca",
                "Gales": "Galce",
                "Georgiano": "Gürcüce",
                "Griego": "Yunanca",
                "Hindi": "Hintçe",
                "Hungaro": "Macarca",
                "Ingles": "İngilizce",
                "Islandes": "İzlandaca",
                "Japones": "Japonca",
                "Katakana": "Katakana",
                "Kannada": "Kannada",
                "Khmer": "Kmerce",
                "Leton": "Letonca",
                "Lituano": "Litvanca",
                "Numeros/especiales": "Sayılar/özel",
                "Polaco": "Lehçe",
                "Portugues": "Portekizce",
                "Rumano": "Romence",
                "Ruso": "Rusça",
                "Thai": "Tayca",
                "Tibetano": "Tibetçe",
                "Turco": "Türkçe",
                "Vietnamita": "Vietnamca",
            },
            "한국어": {
                "112": '백십이',
                "(2, 56)": "(이, 오십육)", "(4, 28)": "(사, 이십팔)", "(7, 16)": "(칠, 십육)", 
                "(8, 14)": "(팔, 십사)", "(14, 8)": "(십사, 팔)", "(16, 7)": "(십육, 칠)", 
                "(28, 4)": "(이십팔, 사)", "(3, 56)": "(삼, 오십육)", "(4, 56)": "(사, 오십육)", 
                "(5, 56)": "(오, 오십육)", "(7, 56)": "(칠, 오십육)", "(8, 56)": "(팔, 오십육)", 
                "(10, 56)": "(십, 오십육)", "(11, 56)": "(십일, 오십육)", "(14, 56)": "(십사, 오십육)",
                "titulo_cifrar_descifrar": "암호화 또는 복호화",
                "opcion_cifrar": "암호화",
                "opcion_descifrar": "복호화",
                "boton_aceptar": "확인",
                "seleccionar_fichero": "파일 선택",
                "cifrado": "암호화",
                "descifrado": "복호화",
                "descifrado_guardado": "복호화된 파일이 저장되었습니다.",
                "bytes": "바이트",
                "total_caracteres_original": "원본 문자 총계",
                "total_caracteres_hexadecimal": "16진수 문자 총계",
                "convertido_a_hexadecimal": "16진수로 변환됨",
                "archivo_temporal_creado": "임시 파일이 생성되었습니다",
                "insertar_referencia_titulo": "참조 삽입",
                "insertar_referencia_mensaje": "참조를 입력하세요 (공백 없이):",
                "referencia_encontrada_eliminada": "참조가 발견되어 삭제되었습니다. 성공.",
                "referencia_no_encontrada": "참조를 찾을 수 없습니다.",
                "no_procesar_archivo": "파일을 처리할 수 없습니다",
                "archivo_temporal_eliminado": "임시 파일이 삭제되었습니다",
                "archivo_guardado": "파일이 성공적으로 저장되었습니다",
                "cajas_vacias": "상자를 비울 수 없습니다",
                "cargar_fichero": "파일 로드",
                "cifrado_guardado": "암호화가 16진수 형식으로 저장되었습니다",
                "cifrado_realizado": "암호화 완료",
                "contenido_guardado": "내용이 저장되었습니다",
                "descifrado_guardado_original": "복호화가 원본 형식으로 저장되었습니다",
                "descifrado_realizado": "복호화 완료",
                "error_hex_impar": "16진수 내용에 짝수 개의 문자가 없습니다.",
                "exito": "성공",
                "extension_mensaje": "원본 파일의 확장자를 입력하세요(예: .png, .jpg, .txt):",
                "extension_titulo": "파일 확장자",
                "file_encryption": "파일 암호화",
                "guardar": "저장",
                "hex_invalido": "16진수 내용이 유효하지 않아 이진수로 변환할 수 없습니다.",
                "ingrese_numeros": "모든 상자에 숫자만 입력하고 빈 상자가 없는지 확인하세요.",
                "invalid_hex": "16진수 내용에 짝수 개의 문자가 없습니다.",
                "nocontenido": "처리할 내용이 없습니다",
                "no_cargar_archivo": "파일을 로드할 수 없습니다",
                "noguardar": "파일을 저장할 수 없습니다.",
                "seleccionar_fichero": "파일 선택",
                "tamano_archivo": "파일 크기",
                "temp_file_creado": "임시 파일 생성됨",
                "temp_file_deleted": "임시 파일 삭제됨",
                "total_caracteres": "총 문자 수",
                "aceptar": "수락",
                "advertencia": "문자 삽입 오류.",
                "advertencia1": "문자 '{}'은(는) 이미 사용되었습니다",
                "advertencia2": "문자 제한을 초과했습니다. 초과된 문자는 삭제됩니다.",
                "agregar_todos": "모두 추가",
                "ajustes": "설정",
                "aleatoriedad": "무작위화",
                "borrar_caracter": "마지막 문자 삭제",
                "cambiar_tamano_letra": "글자 크기 변경",
                "cambiar_idioma": "언어 변경",
                "cancelar": "취소",
                "caracteres": "문자",
                "caracteres_idiomas": "언어 문자",
                "caracteres_restantes": "남은 문자",
                "caracteres_por_idiomas": "언어별 문자",
                "cifrar": "암호화",
                "cifrar_texto": "텍스트 암호화",
                "confirmar": "확인",
                "confirmar_eliminar_plantilla": "템플릿 삭제 확인",
                "consejos": "팁",
                "contraseña_requerida": "비밀번호 필요",
                "crear_plantilla": "템플릿 만들기",
                "creditos": "크레딧",
                "descifrar": "복호화",
                "descifrar_texto": "텍스트 복호화",
                "editar": "편집",
                "editar_plantilla": "템플릿 편집",
                "editar_plantilla_existente": "기존 템플릿 편집",
                "ejecutar": "실행",
                "eliminar": "삭제",
                "error": "오류",
                "error_ingresar_valores": "모든 값을 입력해주세요.",
                "error_valores_numeros": "값은 영 에서 천 사이의 숫자여야 합니다.",
                "excedido_intentos_mensaje": "최대 시도 횟수를 초과했습니다. 장치가 폭발하도록 전압 과열이 실행되었습니다...",
                "faq": "자주 묻는 질문",
                "formato_invalido": "잘못된 템플릿 형식입니다. 쉼표로 구분된 문자 목록인지 확인하세요.",
                "gestionar_plantillas": "템플릿 관리",
                "guardar_plantilla": "템플릿 저장",
                "guardada_correctamente": "템플릿 '{}'이(가) 성공적으로 저장되었습니다",
                "ingresa_contraseña": "비밀번호 입력",
                "ingrese_nombre_plantilla": "템플릿의 이름을 입력하세요",
                "info": "템플릿 생성",
                "info2": "옵션 선택",
                "info3": "템플릿 삭제",
                "info_funcion_no_implementada": "옵션을 선택하지 않았습니다 암호화, 복호화 또는 템플릿 관리.",
                "intenta_nuevamente": "비밀번호 오류, 다시 시도하세요",
                "licencia": "라이선스",
                "limpiar": "지우기",
                "No_hay_plantillas_nuevas_creadas_para_editar": "편집할 새로 생성된 템플릿이 없습니다",
                "No_plantilla_seleccionada_no_existe": "선택된 템플릿이 없거나 템플릿이 존재하지 않습니다",
                "Nueva_plantilla_creada": "새 템플릿 생성됨",
                "numero_invalido": "유효한 숫자를 입력해 주세요",
                "Numeros/signos": "숫자/기호",
                "Plantilla_1": "라틴",
                "Plantilla_2": "유라시아",
                "Plantilla_3": "아랍어, 암하라어, 체로키어",
                "Plantilla_4": "중국어",
                "Plantilla_5": "아시아",
                "plantilla_eliminada": "템플릿 '{}'이(가) 삭제되었습니다",
                "plantilla_en_construccion": "제작 중인 템플릿",
                "plantilla_no_coincide": "템플릿이 일치하지 않습니다",
                "salir": "나가기",
                "Selecciona_la_plantilla_a_editar": "편집할 템플릿 선택",
                "seleccionar_plantilla": "템플릿 선택",
                "seleccionar_tamaño": "크기 선택",
                "seleccione_idiomas": "언어 선택",
                "Signos": "기호",
                "solicitar_contraseña": "비밀번호 입력",
                "tamano_fuera_rango": "크기는 팔 에서 이십사 사이여야 합니다",
                "texto": "텍스트",
                "titulo": "LIVENCRYPT 1.1",
                "valor_1": "하나의 가치",
                "valor_2": "둘의 가치",
                "valor_3": "셋의 가치",
                "valor_4": "넷의 가치",
                "valor_5": "다섯의 가치",
                "Aleman": "독일어",
                "Amharico": "암하라어",
                "Arabe_clasico": "고전 아랍어",
                "Arabigos": "아라비아 숫자",
                "Armenio": "아르메니아어",
                "Bengali": "벵골어",
                "Birmano": "버마어",
                "Cherokee": "체로키어",
                "Checo": "체코어",
                "Chino": "중국어",
                "Coreano": "한국어",
                "Devanagari": "데바나가리",
                "Escandinavo": "스칸디나비아어",
                "Espanol": "스페인어",
                "Etiope": "에티오피아어",
                "Frances": "프랑스어",
                "Gales": "웨일스어",
                "Georgiano": "조지아어",
                "Griego": "그리스어",
                "Hindi": "힌디어",
                "Hungaro": "헝가리어",
                "Ingles": "영어",
                "Islandes": "아이슬란드어",
                "Japones": "일본어",
                "Katakana": "가타카나",
                "Kannada": "칸나다어",
                "Khmer": "크메르어",
                "Leton": "라트비아어",
                "Lituano": "리투아니아어",
                "Numeros/especiales": "숫자/특수",
                "Polaco": "폴란드어",
                "Portugues": "포르투갈어",
                "Rumano": "루마니아어",
                "Ruso": "러시아어",
                "Thai": "태국어",
                "Tibetano": "티베트어",
                "Turco": "터키어",
                "Vietnamita": "베트남어",
            }
        }
        
        # Definir los teclados aquí
        self.teclados = {
            "Plantilla_1": {
                "nombre": "Plantilla_1",
                "layout": [
                    ["ཁ", "བ", "3", "s", "ཡ", "ā", "y", "v", "×", "ç", "ឃ", "m", "ń", "ཞ", "»", ";", "z", "ř", "บ", "ø", "ş", "ན", "t", "丽", "ཧ", "0", ">", "ཅ", "ő", "ï", "œ", "ད", "ý", "í", "ž", "ཐ", "ཉ", "+", "ù", "ē", "ņ", "k", "ț", "į", "ལ", "«", "1", "ห", "ů", "ཏ", "i", "ô", "ğ", "â", "û", "ཚ"],
                    ["æ", "ག", "ß", "š", "x", "ང", "e", "ж", "b", "ň", "ค", "ར", "ć", "ཕ", "ż", "ཝ", "l", "<", "མ", "л", "ģ", "à", "d", "h", "9", "j", "5", "ធ", "f", "-", "w", "g", "þ", "ą", "n", "ཇ", "ö", "?", "2", '␣', "c", "ष", "ŵ", "î", "4", ",", "ಟ", "ཛ", "ཙ", "ł", "p", "7", "÷", "å", "ü", "ä"],
                    ["ཤ", "ಬ", "¡", "ཀ", "ș", "ŷ", "ú", "q", "ź", "པ", "¿", "(", "チ", "a", "エ", ".", "ś", "ཆ", "ñ", "ベ", "ķ", "á", "é", "ཟ", "ཨ", "ė", "ê", "ỳ", "ས", "ű", "ă", "č", "ð", "ū", "ď", "ě", "o", "6", "ť", "8", "u", "r", "ī", "ಌ", "!", "è", ":", "ę", ")", "=", "ó", "ф", "ı", "འ", "ë", "丝"],  
                                        ]
            },
            "Plantilla_2": {
                "nombre": "Plantilla_2",
                "layout": [
                    ["с", "თ", "?", "з", "ფ", "ζ", "ղ", "д", "և", "ღ", "υ", "ю", "ц", "პ", "ա", "п", "？", "ը", "թ", "ო", "4", "հ", "9", "ჯ", "դ", "ъ", ">", "р"],
                    ["დ", "÷", "г", "ի", "¿", "ლ", "э", "ժ", "0", ":", "л", "λ", "յ", "უ", "ց", "բ", "ե", "ր", "պ", "ვ", "խ", "1", "ს", "ш", "œ", "5", "»", "ճ"],
                    ["ტ", "ა", ";", "π", "փ", ")", "გ", "ნ", "մ", "ე", "<", "«", "о", "ყ", "-", "к", "б", "η", "β", "ռ", "æ", "ჟ", "ջ", "ո", "=", "ქ", "ზ", "ы"],
                    ["и", "·", "č", "ծ", "я", "շ", "7", "δ", "у", "ν", "ბ", "w", "რ", "8", "ჭ", "ι", "м", "ძ", "ω", "შ", "ն", "ჰ", "(", "ь", "¡", "ф", "χ", '␣'],
                    ["ρ", "т", "მ", "!", "е", "а", "й", "+", "ი", "ც", "ч", "լ", "ձ", "н", "ñ", "է", "წ", "ւ", "ж", "վ", "ხ", "օ", "γ", "6", "ŵ", "կ", "ֆ", "в"],
                    ["α", "տ", "չ", "×", "ჩ", "3", ".", "τ", "ο", "զ", "ս", "ք", "ß", "щ", "φ", "μ", "ё", "ε", "σ", "ξ", "კ", "х", "գ", "2", "κ", "ψ", "θ", "ž"],
                ]
            },            
            "Plantilla_3": {
                "nombre": "Plantilla_3",
                "layout": [
                    ["Ꮝ", "٨", "ዡ", "?", "ཏ", "Ꮋ", "ሖ", "፬", "ጼ", "Ꮿ", "ሴ", "٩", "ፁ", "ዩ", "Ꮑ", "ሃ", "ፍ", "Ꭳ", "ፃ", "ب", "د", "ቲ", "Ꭷ", "ጂ", "=", "ዕ", "Ꮒ", "ዥ", "१", "Ꮁ", "ኘ", "ى", "ጱ", "Ꮙ", "Ꮛ", "የ", "+", "ጮ", "ኪ", "ቶ", "ሉ", "ሻ", "ኔ", "ኩ", "፰", "ቁ", "Ꮞ", "٧", "ع", "በ", "ሾ", "པ", "ር", "ኮ", "Ꭺ", "ذ"],
                    ["Ꭴ", "ཇ", "ཝ", "ن", "ባ", "ራ", "ፐ", "ཟ", "غ", "ዱ", "ዢ", "ሒ", "·", "ك", "ཤ", "Ꮭ", "ت", "ፆ", "ሤ", "ኀ", "ሐ", "፩", "ጴ", "Ꮤ", "خ", "ኻ", "ཙ", "ጁ", "ጪ", "ጒ", "ག", "ጀ", "ጹ", "ከ", "Ꮢ", "Ꮄ", "Ꮼ", "Ꭸ", "ጳ", "ቂ", "ች", "ሱ", ")", "ص", "ዦ", "ሣ", "Ꮬ", "0", "Ᏺ", "ኦ", "ፋ", "ፂ", "ዶ", "3", "Ꮷ", "Ꮥ"],
                    ["ጕ", "ሸ", "ሥ", "Ꭻ", "ཨ", "፲", "ተ", "አ", "ፎ", "ፅ", "ጔ", "ጰ", "Ꮲ", "ፌ", "ق", "Ꮗ", "Ꮎ", "འ", "-", "ሽ", "Ꮨ", "ቹ", "ኤ", "ዠ", "Ꮸ", "፪", "ጡ", "ቡ", "ኄ", "ዬ", "Ꮾ", "ན", "ዑ", "ቀ", "Ꭾ", "ج", "ፒ", "ሠ", "Ꮆ", "ሕ", "ፑ", "ል", "ቺ", "ኆ", "ሪ", "Ꮟ", "ཡ", "٦", "ጤ", "ነ", "ደ", "ዖ", "ሹ", "4", "ض", "ጶ"],
                    ["Ꮕ", "ቍ", "Ꭰ", "ቄ", "ኝ", "Ꮳ", "ታ", "Ꮓ", "ፉ", "ቼ", "ቅ", "ጾ", "Ꮪ", "ቱ", "ኙ", "ፖ", "ቤ", "ክ", "ላ", "ሶ", "ሙ", "Ꮹ", "Ꮯ", "ኜ", "Ꮽ", "٠", "ቊ", "ཅ", "ፔ", "ዤ", "Ꮶ", "ጩ", "ཞ", "፯", "ད", "Ꮊ", "ሡ", "ཚ", "ያ", "ፚ", "<", "ར", "ዮ", "ዜ", "Ꮘ", "ཉ", ":", "ሔ", "Ᏼ", "ሂ", "ጺ", "ጸ", "ቈ", "آ", "ው", "ئ"],
                    ["ሌ", "9", "Ꮻ", "ን", "ኼ", "ጊ", "ሰ", "8", "ኁ", "٣", "Ꮱ", "Ꮀ", "ف", "ቌ", "ካ", "×", "Ꭼ", "1", "ጐ", "ኡ", "Ꮴ", "Ꮦ", "ዣ", "ሦ", "ፊ", '␣', "Ꮉ", "إ", "ና", "ቢ", "ኺ", "Ꮫ", "ཐ", "ي", "ሢ", "ሼ", "ጆ", "ጉ", "!", "ም", "ዉ", "ዪ", "ዳ", "ፀ", "ة", "ཆ", "ጢ", "ጵ", "ሳ", "Ꭹ", "ء", "ስ", "ا", "ጅ", "م", "ز"],
                    ["ህ", "ጃ", "ث", "ዛ", "መ", "ས", "١", "ሀ", "ዘ", "ቃ", "٥", "ሞ", "Ꮧ", "Ꮵ", "ዝ", "ዴ", "ሬ", "ቸ", "ኃ", "ጭ", "Ꮌ", "ሜ", "ቾ", "ሁ", "Ꭿ", "ጦ", "མ", "ዐ", "ፙ", "ብ", "ወ", "ሆ", "ዌ", "٤", "Ꮈ", "ኸ", "Ꮣ", "ጓ", "ጽ", "ང", "Ꮮ", ".", "ሩ", "٢", "ཁ", "÷", "ጥ", "ሺ", "ት", "ኽ", "¡", "ዒ", "ጋ", "Ᏸ", "ረ", "ቆ"],
                    ["ፕ", "ኒ", "أ", "ጌ", "ጬ", ">", "ጫ", "Ꮚ", "5", "ኚ", "Ꮏ", "ፈ", "ظ", "እ", "و", "Ꮺ", "Ꮃ", "ሲ", "؟", "ལ", "ፓ", "ጻ", "ཀ", "Ꭵ", "Ꭽ", "ቦ", "ጨ", "ዓ", "ዔ", "፮", "ዚ", "ጲ", "ኞ", "Ꮍ", "Ꮖ", "ግ", "6", "ዲ", "Ꮠ", "ؤ", "ቴ", "ጣ", "፱", "؛", "Ꭱ", "«", "2", "ጄ", "س", "Ꮇ", "ይ", "ኬ", "Ꭲ", "ه", "»", "ለ"],
                    ["ر", "ሮ", "Ᏹ", "ཧ", "ዊ", "ሑ", ";", "Ꮂ", "ሚ", "Ꮐ", "ጎ", "ኑ", "፫", "ዎ", "ش", "ሊ", "፭", "ኾ", "ቻ", "ኣ", "ድ", "ل", "ཛ", "ማ", "ቋ", "7", "ሄ", "ሓ", "ኅ", "ኛ", "Ꮩ", "ዋ", "ኂ", "ጠ", "ཕ", "ኢ", "Ꮜ", "¿", "Ꮡ", "Ꮰ", "Ꮔ", "ዙ", "(", "Ꮅ", "ح", "Ꭶ", "？", "ኹ", "ሎ", "Ᏻ", "ፄ", "ገ", "བ", "ط", "ዞ", "ኖ"],
                ]
            },           
            "Plantilla_4": {
                "nombre": "Plantilla_4",
                "layout": [
                    ["冕", "亿", "令", "咙", "冒", "佥", "参", "凉", "兆", "关", "仓", "凳", "假", "亍", "事", "兽", "住", "呲", "也", "傩", "制", "侮", "叵", "仅", "兔", "口", "反", "乌"],
                    ["咝", "剁", "便", "侦", "乱", "叻", "乡", "四", "入", "僖", "元", "册", "傲", "ಜ", "俞", "到", "叁", "傅", "吩", "候", "俣", "ヤ", "买", "东", "冠", "丫", "伊", "倔"],
                    ["享", "偎", "伸", "倜", "伎", "俟", "俸", "么", "卸", "侧", "吴", "剂", "凛", "亠", "劁", "剧", "佾", "伐", "仟", "即", "升", "勖", "剿", "亻", "乎", "勃", "伧", "冀"],
                    ["刂", "勰", "危", "古", "中", "凇", "厥", "击", "ค", "卜", "佩", "咒", "匀", "件", "且", "台", "倨", "丛", "免", "ㅈ", "君", "匠", "久", "刚", "务", "傍", "吾", "俐"],
                    ["促", "倭", "周", "勿", "兵", "乔", "ར", "侠", "匙", "俦", "六", "冗", "佶", "丙", "使", "互", "原", "具", "匣", "伫", "侪", "卡", "俗", "命", "咄", "八", "厂", "佞"],
                    ["南", "佼", "亚", "受", "吖", "之", "兀", "单", "仍", "九", "刀", "似", "刳", "剐", "伪", "咣", "于", "兄", "亮", "十", "吻", "倍", "吏", "刎", "倮", "凿", "冈", "乍"],
                    ["佗", "呤", "劫", "倏", "卧", "叟", "傣", "名", "依", "仪", "勒", "他", "劲", "僵", "呒", "借", "亥", "刈", "卤", "匹", "咎", "价", "卷", "咩", "ཤ", "凄", "乃", "侈"],
                    ["吊", "仵", "亩", "伴", "亟", "佰", "್", "吉", "刑", "凰", "充", "呶", "俑", "冯", "呈", "供", "倦", "冥", "伟", "ཆ", "剖", "厢", "右", "丽", "厕", "ㅘ", "匦", "剡"],
                    ["咀", "丨", "佬", "仫", "党", "刺", "刭", "从", "刨", "叙", "吞", "云", "仗", "呐", "吐", "刘", "卫", "冼", "吲", "偻", "二", "呼", "儇", "卟", "僦", "呢", "又", "介"],
                    ["匕", "俪", "刹", "乾", "倩", "则", "傀", "呕", "些", "勹", "丐", "卿", "冉", "吁", "两", "企", "佐", "厨", "呸", "华", "个", "伺", "份", "兴", "冢", "凋", "办", "厩"],
                    ["仡", "剩", "例", "凭", "味", "吗", "业", "勐", "侬", "ཀ", "匈", "倾", "厮", "员", "伙", "和", "仿", "ཚ", "倬", "与", "佚", "乏", "公", "亦", "吡", "劓", "仑", "劾"],
                    ["伶", "今", "匐", "吨", "咋", "ム", "偾", "咧", "凸", "伯", "叫", "光", "亨", "历", "及", "动", "侉", "佧", "匮", "吱", "募", "匿", "厘", "乳", "佻", "亓", "俾", "劭"],
                    ["凡", "刖", "仃", "吠", "偰", "伤", "匍", "儡", "勤", "合", "凵", "印", "吆", "冶", "召", "乓", "向", "咦", "兰", "别", "俱", "勋", "咇", "伉", "吝", "〇", "占", "乂"],
                    ["匪", "初", "劂", "各", "压", "剔", "冰", "卒", "叹", "剑", "凼", "函", "刮", "刻", "卄", "吟", "半", "但", "叨", "剃", "倘", "人", "养", "亲", "变", "取", "吃", "判"],
                    ["冱", "你", "况", "倥", "允", "佴", "俨", "劬", "后", "保", "众", "五", "主", "交", "侏", "包", "咏", "侣", "兼", "佃", "另", "僮", "偷", "ཨ", "亵", "吒", "功", "仉"],
                    ["吭", "厦", "友", "侄", "俳", "呱", "佇", "乩", "ธ", "北", "丑", "习", "典", "丸", "举", "伞", "下", "冁", "侑", "佛", "吣", "ザ", "双", "冤", "俅", "兑", "卣", "卞"],
                    ["句", "叉", "俘", "兢", "删", "卢", "割", "助", "仄", "仆", "加", "分", "僧", "专", "凫", "卩", "剌", "只", "傻", "卵", "刷", "告", "吓", "凝", "呆", "俩", "利", "催"],
                    ["ಫ", "叛", "兜", "偈", "卑", "司", "呓", "前", "凶", "劈", "倡", "侯", "史", "呃", "刊", "ヂ", "世", "偕", "ボ", "呗", "叮", "咡", "儋", "做", "优", "冲", "叼", "伏"],
                    ["卯", "卉", "作", "县", "偶", "何", "僭", "仲", "势", "咕", "乙", "号", "叭", "劳", "伦", "丢", "仙", "乘", "再", "呖", "冏", "听", "京", "冬", "一", "侵", "匆", "停"],
                    ["低", "任", "偃", "仂", "乐", "仰", "丘", "估", "丧", "内", "傧", "伛", "呙", "厍", "ಪ", "俎", "发", "亳", "亭", "僳", "僚", "咨", "启", "克", "凯", "仇", "净", "乇"],
                    ["咖", "佣", "仳", "军", "剽", "同", "呛", "佤", "亢", "叩", "儆", "叽", "呋", "剜", "为", "亘", "咐", "厉", "倚", "叱", "丹", "含", "凤", "厶", "券", "劢", "付", "儿"],
                    ["卖", "ㅙ", "凑", "励", "僬", "伢", "刃", "ಧ", "厄", "咛", "吼", "丞", "咤", "削", "勾", "吧", "共", "咆", "串", "佳", "努", "七", "佝", "储", "乜", "咔", "丰", "呜"],
                    ["副", "仔", "吕", "佟", "决", "剞", "吸", "先", "厝", "侨", "仞", "化", "农", "予", "傥", "劝", "准", "余", "伽", "偲", "勘", "列", "匡", "上", "呀", "卦", "刁", "俏"],
                    ["可", "划", "位", "吮", "兹", "仨", "午", "傺", "体", "厅", "卓", "丁", "丝", "俜", "千", "力", "几", "伍", "创", "呻", "劐", "侍", "医", "出", "井", "什", "丕", "匝"],
                    ["剪", "其", "劣", "呦", "偏", "协", "减", "叠", "叔", "兕", "倪", "ས", "凹", "丈", "厚", "匾", "倌", "卮", "厌", "修", "像", "冽", "俊", "倒", "剥", "争", "咂", "ಞ"],
                    ["严", "呔", "休", "了", "切", "丶", "ต", "亏", "万", "侩", "勉", "三", "咪", "乒", "厣", "书", "勺", "去", "俺", "仁", "吵", "佯", "エ", "值", "咚", "临", "俯", "佑"],
                    ["传", "健", "区", "偿", "刍", "偌", "全", "呷", "儒", "侔", "侗", "僻", "凌", "勇", "叶", "否", "兖", "仕", "乞", "傈", "冷", "偬", "债", "俚", "却", "侃", "匏", "写"],
                    ["乖", "伥", "俭", "俄", "冂", "吹", "代", "侥", "ペ", "冖", "ヨ", "博", "以", "呵", "亡", "产", "刽", "兮", "冫", "卅", "佘", "不", "义", "会", "们", "信", "卺", "ཁ"],
                ]
            },           
            "Plantilla_5": {
                "nombre": "Plantilla_5",
                "layout": [
                    ['8','অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'ঌ', 'এ', 'ঐ', 'ও', 'ঔ', 'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ', 'ট', 'ঠ', 'ড', 'ঢ', 'ণ', 'ত', 'থ', 'দ', 'ধ', 'ন', 'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ', 'স', 'হ', 'ড়', 'ঢ়', 'য়', 'ৎ', 'ং', 'ঃ', 'ঁ', 'ৰ', 'ৱ', 'ৠ', 'ৡ', 'ㅄ'],
                    ['9','က', 'ခ', 'ဂ', 'ဃ', 'င', 'စ', 'ဆ', 'ဇ', 'ဈ', 'ဉ', 'ည', 'ဋ', 'ဌ', 'ဍ', 'ဎ', 'ဏ', 'တ', 'ထ', 'ဒ', 'ဓ', 'န', 'ပ', 'ဖ', 'ဗ', 'ဘ', 'မ', 'ယ', 'ရ', 'လ', 'ဝ', 'သ', 'ဟ', 'ဠ', 'အ', 'ဣ', 'ဤ', 'ဥ', 'ဦ', 'ဧ', 'ဩ', 'ဪ', 'ဿ', 'ှ', 'ျ', 'ြ', 'ွ', 'ါ', 'ာ', 'ိ', 'ီ', 'ု', 'ူ', 'ေ', 'ဲ','ゴ', 'ザ',],
                    ['。','ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', 'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ', 'ㄳ', 'ㄵ', 'ㄶ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅄ', 'ジ', 'ズ', 'ゼ', 'ゾ', 'ダ'],
                    ['：', 'अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ॠ', 'ऌ', 'ॡ', 'ऍ', 'ऎ', 'ए', 'ऐ', 'ऑ', 'ऒ', 'ओ', 'औ', 'क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न', 'ऩ', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ऱ', 'ल', 'ळ', 'ऴ', 'व', 'श', 'ष', 'स', 'ह', 'क्ष'],
                    ['ー','ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಋ', 'ಌ', 'ಎ', 'ಏ', 'ಐ', 'ಒ', 'ಓ', 'ಔ', 'ಕ', 'ಖ', 'ಗ', 'ಘ', 'ಙ', 'ಚ', 'ಛ', 'ಜ', 'ಝ', 'ಞ', 'ಟ', 'ಠ', 'ಡ', 'ಢ', 'ಣ', 'ತ', 'ಥ', 'ದ', 'ಧ', 'ನ', 'ಪ', 'ಫ', 'ಬ', 'ಭ', 'ಮ', 'ಯ', 'ರ', 'ಱ', 'ಲ', 'ಳ', 'ವ', 'ಶ', 'ಷ', 'ಸ', 'ಹ', 'ಕ್ಷ', 'ಜ್ಞ', 'ಾ', 'ಿ','ឺ', 'ុ',],
                    ['゛','ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ', 'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ヤ', 'ユ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ワ', 'ヲ', 'ン', 'ガ', 'ギ', 'グ', 'ゲ', 'ヂ', 'ヅ', 'デ', 'ド', 'バ', 'ビ'], 
                    ['゜','ក', 'ខ', 'គ', 'ឃ', 'ង', 'ច', 'ឆ', 'ជ', 'ឈ', 'ញ', 'ដ', 'ឋ', 'ឌ', 'ឍ', 'ណ', 'ត', 'ថ', 'ទ', 'ធ', 'ន', 'ប', 'ផ', 'ព', 'ភ', 'ម', 'យ', 'រ', 'ល', 'វ', 'ශ', 'ស', 'ហ', 'ឡ', 'អ', 'ឥ', 'ឦ', 'ឧ', 'ឨ', 'ឩ', 'ឪ', 'ឫ', 'ឬ', 'ឭ', 'ឮ', 'ឯ', 'ឰ', 'ឱ', 'ឲ', 'ឳ', 'ា', 'ិ', 'ី', 'ឹ',  'ូ', 'ួ', 'ើ'],
                    ['〜', 'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ', 'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'เ', 'แ'],
                    ['＿', '০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯', '৳', '৺', '৻', 'ঽ', '।', '॥', 'श्र', 'ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'ॄ', 'ॢ', 'ॣ', 'े', 'ै', 'ो', 'ौ', 'ॅ', 'ॆ', 'ॉ', 'ॊ', '्', 'ं', 'ः', 'ऽ', '़', 'त्र', 'ज्ञ', 'โ', 'ใ', 'ไ', '\u0E50', '\u0E51', '\u0E52', '\u0E53', '\u0E54', '\u0E55', '\u0E56', '\u0E57', '\u0E58', '\u0E59', '\u0E3F', '\u0E4F'],
                    ['7', '၀', '၁', '၂', '၃', '၄', '၅', '၆', '၇', '၈', '၉', '။', '၌', '၏', '္', '့', 'း', '၊', '၍', '၎', 'ံ', '်', 'ၑ', 'ၒ', 'ၓ', 'ၔ', 'ၕ', 'ၖ', 'ၗ', 'ၘ', 'ၙ', 'ឿ', 'ៀ', 'េ', 'ែ', 'ៃ', 'ោ', 'ៅ', 'ំ', 'ះ', 'ៈ', '៉', '៊', '់', '៌', '៍', '៎', '៏', '័', '៑', '្', 'ៗ', 'ៜ', '\u0E46', '\u0E5A', '\u0E5B', 'ヒュ'],
                    ['咔', '零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '億', '兆', '、', '「', '」', '『', '』', '・', '~', '…', '₩', 'ブ', 'ベ', 'ボ', 'パ', 'ピ', 'プ', 'ペ', 'ポ', 'キャ', 'キュ', 'キョ', 'シャ', 'シュ', 'ショ', 'チャ', 'チュ', 'チョ', 'ニャ', 'ニュ', 'ニョ', 'ヒャ', 'ヒョ', 'ミャ', 'ミュ', 'ミョ', 'リャ', 'リュ', 'リョ', 'ギャ', 'ギュ', 'ギョ'],
                    ['吣', '०', '१', '२', '३', '४', '५', '६', '७', '८', '९', 'ॐ', '॰', '₹', '០', '១', '២', '៣', '៤', '៥', '៦', '៧', '៨', '៩', '។', '៕', '៖', '៘', '៙', '៚', '៛', '៝', '៰', '៱', '៲', '៳', '៴', '៵', '៶', '៷', '៸', '៹', '￥', 'ೀ', 'ು', 'ೂ', 'ೃ', 'ೄ', 'ೆ', 'ೇ', 'ೈ', 'ೊ', 'ೋ', 'ೌ', '್', 'ಂ', 'ಃ'],
                    ['吠', '೦', '೧', '೨', '೩', '೪', '೫', '೬', '೭', '೮', '೯', 'ೱ', 'ೲ','␣', '๑', '๓', '๔', '๕', '๖', '๗', '๙', '฿', 'ๆ', '๎', '๚', '๛', '๏', '๐', '๒', '๘', 'ジャ', 'ジュ', 'ジョ', 'ビャ', 'ビュ', 'ビョ', 'ピャ', 'ピュ', 'ピョ', 'ヴ', 'ファ', 'フィ', 'フェ', 'フォ', 'ウィ', 'ウェ', 'ウォ', 'ヵ', 'ヶ', 'ッ', '0', '1', '2', '3', '4', '5', '6'],                    
                ]
            },
            "filelivencrypt": {
                "nombre": "filelivencrypt",
                "layout": [
                    ["ճ", "ц", "a", "բ", "v", "t", "щ", "佻", "ր", "k", "մ", "հ", "z", "j", "л", "乘", "օ", "в", "0", "ծ", "x", "ո", "կ"],
                    ["e", "r", "խ", "п", "h", "м", "q", "չ", "ն", "ч", "а", "ю", "ը", "о", "ы", "р", "к", "ш", "ղ", "я", "u", "ա", "ս"],
                    ["с", "й", "х", "d", "պ", "շ", "д", "ё", "г", "y", "ռ", "վ", "ь", "է", "ե", "4", "7", "և", "յ", "m", "դ", "s", "ց"],
                    ["տ", "и", "փ", "е", "լ", "5", "你", "2", "н", "g", "ք", "т", "у", "1", "զ", "ջ", "n", "ւ", "f", "б", "ձ", "w", "ф"],
                    ["b", "ֆ", "l", "ж", "ժ", "գ", "8", "i", "p", "令", "9", "c", "o", "6", "ի", "3", "թ", "з", "э", "ъ", "俨", "原", "厥"]
                ]
            }
        }
            
        self.plantillas_personalizadas = {}
        
        self.caracteres_por_idioma = {
        "Aleman": ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'ä', 'ö', 'ü', 'ß'],
        "Amharico": ['ሀ', 'ለ', 'ሐ', 'መ', 'ሠ', 'ረ', 'ሰ', 'ሸ', 'ቀ', 'በ', 'ተ', 'ቸ', 'ኀ', 'ነ', 'ኘ', 'አ', 'ከ', 'ኸ', 'ወ', 'ዐ', 'ዘ', 'ዠ', 'የ', 'ደ', 'ጀ', 'ገ', 'ጠ', 'ጨ', 'ጰ', 'ጸ', 'ፀ', 'ፈ', 'ፐ', 'ቈ', 'ቊ', 'ቋ', 'ቌ', 'ቍ', 'ጎ', 'ጐ', 'ጒ', 'ጓ', 'ጔ', 'ጕ', 'ፙ', 'ፚ'],
        "Arabe_clasico": ['\u0627', '\u0628', '\u062A', '\u062B', '\u062C', '\u062D', '\u062E', '\u062F', '\u0630', '\u0631', '\u0632', '\u0633', '\u0634', '\u0635', '\u0636', '\u0637', '\u0638', '\u0639', '\u063A', '\u0641', '\u0642', '\u0643', '\u0644', '\u0645', '\u0646', '\u0647', '\u0648', '\u064A', '\u0621', '\u0622', '\u0623', '\u0625', '\u0624', '\u0626', '\u0629', '\u0649'],
        "Armenio": ['ա', 'բ', 'գ', 'դ', 'ե', 'զ', 'է', 'ը', 'թ', 'ժ', 'ի', 'լ', 'խ', 'ծ', 'կ', 'հ', 'ձ', 'ղ', 'ճ', 'մ', 'յ', 'ն', 'շ', 'ո', 'չ', 'պ', 'ջ', 'ռ', 'ս', 'վ', 'տ', 'ր', 'ց', 'ւ', 'փ', 'ք', 'օ', 'ֆ', 'և'],
        "Bengali": ['অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'ঌ', 'এ', 'ঐ', 'ও', 'ঔ', 'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ', 'ট', 'ঠ', 'ড', 'ঢ', 'ণ', 'ত', 'থ', 'দ', 'ধ', 'ন', 'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ', 'স', 'হ', 'ড়', 'ঢ়', 'য়', 'ৎ', 'ং', 'ঃ', 'ঁ', 'ৰ', 'ৱ', 'ৠ', 'ৡ'],
        "Birmano": ['က', 'ခ', 'ဂ', 'ဃ', 'င', 'စ', 'ဆ', 'ဇ', 'ဈ', 'ဉ', 'ည', 'ဋ', 'ဌ', 'ဍ', 'ဎ', 'ဏ', 'တ', 'ထ', 'ဒ', 'ဓ', 'န', 'ပ', 'ဖ', 'ဗ', 'ဘ', 'မ', 'ယ', 'ရ', 'လ', 'ဝ', 'သ', 'ဟ', 'ဠ', 'အ', 'ဣ', 'ဤ', 'ဥ', 'ဦ', 'ဧ', 'ဩ', 'ဪ', 'ဿ', 'ှ', 'ျ', 'ြ', 'ွ', 'ါ', 'ာ', 'ိ', 'ီ', 'ု', 'ူ', 'ေ', 'ဲ', 'ံ', '်', 'ၑ', 'ၒ', 'ၓ', 'ၔ', 'ၕ', 'ၖ', 'ၗ', 'ၘ', 'ၙ'],
        "Cherokee": ['Ꭰ', 'Ꭱ', 'Ꭲ', 'Ꭳ', 'Ꭴ', 'Ꭵ', 'Ꭶ', 'Ꭷ', 'Ꭸ', 'Ꭹ', 'Ꭺ', 'Ꭻ', 'Ꭼ', 'Ꭽ', 'Ꭾ', 'Ꭿ', 'Ꮀ', 'Ꮁ', 'Ꮂ', 'Ꮃ', 'Ꮄ', 'Ꮅ', 'Ꮆ', 'Ꮇ', 'Ꮈ', 'Ꮉ', 'Ꮊ', 'Ꮋ', 'Ꮌ', 'Ꮍ', 'Ꮎ', 'Ꮏ', 'Ꮐ', 'Ꮑ', 'Ꮒ', 'Ꮓ', 'Ꮔ', 'Ꮕ', 'Ꮖ', 'Ꮗ', 'Ꮘ', 'Ꮙ', 'Ꮚ', 'Ꮛ', 'Ꮜ', 'Ꮝ', 'Ꮞ', 'Ꮟ', 'Ꮠ', 'Ꮡ', 'Ꮢ', 'Ꮣ', 'Ꮤ', 'Ꮥ', 'Ꮦ', 'Ꮧ', 'Ꮨ', 'Ꮩ', 'Ꮪ', 'Ꮫ', 'Ꮬ', 'Ꮭ', 'Ꮮ', 'Ꮯ', 'Ꮰ', 'Ꮱ', 'Ꮲ', 'Ꮳ', 'Ꮴ', 'Ꮵ', 'Ꮶ', 'Ꮷ', 'Ꮸ', 'Ꮹ', 'Ꮺ', 'Ꮻ', 'Ꮼ', 'Ꮽ', 'Ꮾ', 'Ꮿ', 'Ᏸ', 'Ᏹ', 'Ᏺ', 'Ᏻ', 'Ᏼ'],
        "Checo": ['a', 'á', 'b', 'c', 'č', 'd', 'ď', 'e', 'é', 'ě', 'f', 'g', 'h', 'i', 'í', 'j', 'k', 'l', 'm', 'n', 'ň', 'o', 'ó', 'p', 'q', 'r', 'ř', 's', 'š', 't', 'ť', 'u', 'ú', 'ů', 'v', 'w', 'x', 'y', 'ý', 'z', 'ž'],
        "Chino": ['〇', '一', '丁', '七', '万', '丈', '三', '四', '上', '下', '不', '与', '丐', '丑', '专', '且', '丕', '世', '丘', '丙', '业', '丛', '东', '丝', '丞', '丢', '两', '严', '丧', '丨', '个', '丫', '中', '丰', '串', '临', '丶', '丸', '丹', '为', '主', '丽', '举', '乂', '乃', '久', '乇', '么', '义', '之', '乌', '乍', '乎', '乏', '乐', '乒', '乓', '乔', '乖', '乘', '乙', '乜', '九', '乞', '也', '习', '乡', '书', '乩', '买', '乱', '乳', '乾', '了', '予', '争', '事', '二', '亍', '于', '亏', '云', '互', '亓', '五', '井', '亘', '亚', '些', '亟', '亠', '亡', '亢', '交', '亥', '亦', '产', '亨', '亩', '享', '京', '亭', '亮', '亲', '亳', '亵', '人', '亻', '亿', '什', '仁', '仂', '仃', '仄', '仅', '仆', '仇', '仉', '今', '介', '仍', '从', '仑', '仓', '仔', '仕', '他', '仗', '付', '仙', '仞', '仟', '仡', '代', '令', '以', '仨', '仪', '仫', '们', '仰', '仲', '仳', '仵', '件', '价', '任', '份', '仿', '企', '伉', '伊', '伍', '伎', '伏', '伐', '休', '众', '优', '伙', '会', '伛', '伞', '伟', '传', '伢', '伤', '伥', '伦', '伧', '伪', '伫', '伯', '估', '伴', '伶', '伸', '伺', '似', '伽', '佃', '但', '佇', '位', '低', '住', '佐', '佑', '体', '何', '佗', '佘', '余', '佚', '佛', '作', '佝', '佞', '佟', '你', '佣', '佤', '佥', '佧', '佩', '佬', '佯', '佰', '佳', '佴', '佶', '佻', '佼', '佾', '使', '侃', '侄', '侈', '侉', '例', '侍', '侏', '侑', '侔', '侗', '供', '依', '侠', '侣', '侥', '侦', '侧', '侨', '侩', '侪', '侬', '侮', '侯', '侵', '便', '促', '俄', '俅', '俊', '俎', '俏', '俐', '俑', '俗', '俘', '俚', '俜', '保', '俞', '俟', '信', '俣', '俦', '俨', '俩', '俪', '俭', '修', '俯', '俱', '俳', '俸', '俺', '俾', '倌', '倍', '倏', '倒', '倔', '倘', '候', '倚', '倜', '借', '倡', '倥', '倦', '倨', '倩', '倪', '倬', '倭', '倮', '债', '值', '倾', '偃', '假', '偈', '偌', '偎', '偏', '偕', '做', '停', '健', '偬', '偰', '偲', '偶', '偷', '偻', '偾', '偿', '傀', '傅', '傈', '傍', '傣', '傥', '傧', '储', '傩', '催', '傲', '傺', '傻', '像', '僖', '僚', '僦', '僧', '僬', '僭', '僮', '僳', '僵', '僻', '儆', '儇', '儋', '儒', '儡', '儿', '兀', '允', '元', '兄', '充', '兆', '先', '光', '克', '免', '兑', '兔', '兕', '兖', '党', '兜', '兢', '入', '全', '八', '公', '六', '兮', '兰', '共', '关', '兴', '兵', '其', '具', '典', '兹', '养', '兼', '兽', '冀', '冁', '冂', '内', '冈', '冉', '册', '再', '冏', '冒', '冕', '冖', '冗', '写', '军', '农', '冠', '冢', '冤', '冥', '冫', '冬', '冯', '冰', '冱', '冲', '决', '况', '冶', '冷', '冼', '冽', '净', '凄', '准', '凇', '凉', '凋', '凌', '减', '凑', '凛', '凝', '几', '凡', '凤', '凫', '凭', '凯', '凰', '凳', '凵', '凶', '凸', '凹', '出', '击', '凼', '函', '凿', '刀', '刁', '刂', '刃', '分', '切', '刈', '刊', '刍', '刎', '刑', '划', '刖', '列', '刘', '则', '刚', '创', '初', '删', '判', '刨', '利', '别', '刭', '刮', '到', '刳', '制', '刷', '券', '刹', '刺', '刻', '刽', '剁', '剂', '剃', '削', '剌', '前', '剐', '剑', '剔', '剖', '剜', '剞', '剡', '剥', '剧', '剩', '剪', '副', '割', '剽', '剿', '劁', '劂', '劈', '劐', '劓', '力', '劝', '办', '功', '加', '务', '劢', '劣', '动', '助', '努', '劫', '劬', '劭', '励', '劲', '劳', '劾', '势', '勃', '勇', '勉', '勋', '勐', '勒', '勖', '勘', '募', '勤', '勰', '勹', '勺', '勾', '勿', '匀', '包', '匆', '匈', '匍', '匏', '匐', '匕', '化', '北', '匙', '匝', '匠', '匡', '匣', '匦', '匪', '匮', '匹', '区', '医', '匾', '匿', '十', '千', '卄', '卅', '升', '午', '卉', '半', '华', '协', '卑', '卒', '卓', '单', '卖', '南', '博', '卜', '卞', '卟', '占', '卡', '卢', '卣', '卤', '卦', '卧', '卩', '卫', '卮', '卯', '印', '危', '即', '却', '卵', '卷', '卸', '卺', '卿', '厂', '厄', '厅', '历', '厉', '压', '厌', '厍', '厕', '厘', '厚', '厝', '原', '厢', '厣', '厥', '厦', '厨', '厩', '厮', '厶', '去', '县', '叁', '参', '又', '叉', '及', '友', '双', '反', '发', '叔', '取', '受', '变', '叙', '叛', '叟', '叠', '口', '古', '句', '另', '叨', '叩', '只', '叫', '召', '叭', '叮', '可', '台', '叱', '史', '右', '叵', '叶', '号', '司', '叹', '叻', '叼', '叽', '吁', '吃', '各', '吆', '合', '吉', '吊', '同', '名', '后', '吏', '吐', '向', '吒', '吓', '吕', '吖', '吗', '君', '吝', '吞', '吟', '吠', '吡', '吣', '否', '吧', '吨', '吩', '含', '听', '吭', '吮', '启', '吱', '吲', '吴', '吵', '吸', '吹', '吻', '吼', '吾', '呀', '呃', '呆', '呈', '告', '呋', '呐', '呒', '呓', '呔', '呕', '呖', '呗', '员', '呙', '呛', '呜', '呢', '呤', '呦', '周', '呱', '呲', '味', '呵', '呶', '呷', '呸', '呻', '呼', '命', '咀', '咂', '咄', '咆', '咇', '咋', '和', '咎', '咏', '咐', '咒', '咔', '咕', '咖', '咙', '咚', '咛', '咝', '咡', '咣', '咤', '咦', '咧', '咨', '咩', '咪'],
        "Coreano": ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', 'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ', 'ㄳ', 'ㄵ', 'ㄶ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅄ'],
        "Devanagari": ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ॠ', 'ऌ', 'ॡ', 'ऍ', 'ऎ', 'ए', 'ऐ', 'ऑ', 'ऒ', 'ओ', 'औ', 'क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न', 'ऩ', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ऱ', 'ल', 'ळ', 'ऴ', 'व', 'श', 'ष', 'स', 'ह', 'क्ष', 'त्र', 'ज्ञ', 'श्र', 'ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'ॄ', 'ॢ', 'ॣ', 'े', 'ै', 'ो', 'ौ', 'ॅ', 'ॆ', 'ॉ', 'ॊ', '्', 'ं', 'ः', 'ऽ', '़'],
        "Escandinavo": ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'å', 'ä', 'æ', 'ø', 'ö', 'é', 'ð', 'þ'],
        "Espanol": ['a', 'á', 'b', 'c', 'd', 'e', 'é', 'f', 'g', 'h', 'i', 'í', 'j', 'k', 'l', 'm', 'n', 'ñ', 'o', 'ó', 'p', 'q', 'r', 's', 't', 'u', 'ú', 'ü', 'v', 'w', 'x', 'y', 'z', 'ỳ'],
        "Etiope": ['ሀ', 'ሁ', 'ሂ', 'ሃ', 'ሄ', 'ህ', 'ሆ', 'ለ', 'ሉ', 'ሊ', 'ላ', 'ሌ', 'ል', 'ሎ', 'ሐ', 'ሑ', 'ሒ', 'ሓ', 'ሔ', 'ሕ', 'ሖ', 'መ', 'ሙ', 'ሚ', 'ማ', 'ሜ', 'ም', 'ሞ', 'ሠ', 'ሡ', 'ሢ', 'ሣ', 'ሤ', 'ሥ', 'ሦ', 'ረ', 'ሩ', 'ሪ', 'ራ', 'ሬ', 'ር', 'ሮ', 'ሰ', 'ሱ', 'ሲ', 'ሳ', 'ሴ', 'ስ', 'ሶ', 'ሸ', 'ሹ', 'ሺ', 'ሻ', 'ሼ', 'ሽ', 'ሾ','ቀ', 'ቁ', 'ቂ', 'ቃ', 'ቄ', 'ቅ', 'ቆ', 'በ', 'ቡ', 'ቢ', 'ባ', 'ቤ', 'ብ', 'ቦ', 'ተ', 'ቱ', 'ቲ', 'ታ', 'ቴ', 'ት', 'ቶ', 'ቸ', 'ቹ', 'ቺ', 'ቻ', 'ቼ', 'ች', 'ቾ', 'ኀ', 'ኁ', 'ኂ', 'ኃ', 'ኄ', 'ኅ', 'ኆ', 'ነ', 'ኑ', 'ኒ', 'ና', 'ኔ', 'ን', 'ኖ', 'ኘ', 'ኙ', 'ኚ', 'ኛ', 'ኜ', 'ኝ', 'ኞ', 'አ', 'ኡ', 'ኢ', 'ኣ', 'ኤ', 'እ', 'ኦ', 'ከ', 'ኩ', 'ኪ', 'ካ', 'ኬ', 'ክ', 'ኮ', 'ኸ', 'ኹ', 'ኺ', 'ኻ', 'ኼ', 'ኽ', 'ኾ', 'ወ', 'ዉ', 'ዊ', 'ዋ', 'ዌ', 'ው', 'ዎ', 'ዐ', 'ዑ', 'ዒ', 'ዓ', 'ዔ', 'ዕ', 'ዖ', 'ዘ', 'ዙ', 'ዚ', 'ዛ', 'ዜ', 'ዝ', 'ዞ', 'ዠ', 'ዡ', 'ዢ', 'ዣ', 'ዤ', 'ዥ', 'ዦ', 'የ', 'ዩ', 'ዪ', 'ያ', 'ዬ', 'ይ', 'ዮ', 'ደ', 'ዱ', 'ዲ', 'ዳ', 'ዴ', 'ድ', 'ዶ', 'ጀ', 'ጁ', 'ጂ', 'ጃ', 'ጄ', 'ጅ', 'ጆ', 'ገ', 'ጉ', 'ጊ', 'ጋ', 'ጌ', 'ግ', 'ጎ', 'ጠ', 'ጡ', 'ጢ', 'ጣ', 'ጤ', 'ጥ', 'ጦ', 'ጨ', 'ጩ', 'ጪ', 'ጫ', 'ጬ', 'ጭ', 'ጮ', 'ጰ', 'ጱ', 'ጲ', 'ጳ', 'ጴ', 'ጵ', 'ጶ', 'ጸ', 'ጹ', 'ጺ', 'ጻ', 'ጼ', 'ጽ', 'ጾ', 'ፀ', 'ፁ', 'ፂ', 'ፃ', 'ፄ', 'ፅ', 'ፆ', 'ፈ', 'ፉ', 'ፊ', 'ፋ', 'ፌ', 'ፍ', 'ፎ', 'ፐ', 'ፑ', 'ፒ', 'ፓ', 'ፔ', 'ፕ', 'ፖ'],
        "Frances": ['a', 'à', 'â', 'æ', 'b', 'c', 'ç', 'd', 'e', 'é', 'è', 'ê', 'ë', 'f', 'g', 'h', 'i', 'î', 'ï', 'j', 'k', 'l', 'm', 'n', 'o', 'ô', 'œ', 'p', 'q', 'r', 's', 't', 'u', 'ù', 'û', 'ü', 'v', 'w', 'x', 'y', 'z'],
        "Gales": ['a', 'â', 'b', 'c', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'l', 'm', 'n', 'o', 'ô', 'p', 'r', 's', 't', 'u', 'û', 'w', 'ŵ', 'y', 'ŷ'],
        "Georgiano": ['ა', 'ბ', 'გ', 'დ', 'ე', 'ვ', 'ზ', 'თ', 'ი', 'კ', 'ლ', 'მ', 'ნ', 'ო', 'პ', 'ჟ', 'რ', 'ს', 'ტ', 'უ', 'ფ', 'ქ', 'ღ', 'ყ', 'შ', 'ჩ', 'ც', 'ძ', 'წ', 'ჭ', 'ხ', 'ჯ', 'ჰ'],
        "Griego": ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω'],
        "Hungaro": ['a', 'á', 'b', 'c', 'd', 'e', 'é', 'f', 'g', 'h', 'i', 'í', 'j', 'k', 'l', 'm', 'n', 'o', 'ó', 'ö', 'ő', 'p', 'r', 's', 't', 'u', 'ú', 'ü', 'ű', 'v', 'w', 'x', 'y', 'z'],
        "Ingles": ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
        "Islandes": ['a', 'á', 'b', 'd', 'ð', 'e', 'é', 'f', 'g', 'h', 'i', 'í', 'j', 'k', 'l', 'm', 'n', 'o', 'ó', 'p', 'r', 's', 't', 'u', 'ú', 'v', 'x', 'y', 'ý', 'þ', 'æ', 'ö'],
        "Kannada": ['ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಋ', 'ಌ', 'ಎ', 'ಏ', 'ಐ', 'ಒ', 'ಓ', 'ಔ', 'ಕ', 'ಖ', 'ಗ', 'ಘ', 'ಙ', 'ಚ', 'ಛ', 'ಜ', 'ಝ', 'ಞ', 'ಟ', 'ಠ', 'ಡ', 'ಢ', 'ಣ', 'ತ', 'ಥ', 'ದ', 'ಧ', 'ನ', 'ಪ', 'ಫ', 'ಬ', 'ಭ', 'ಮ', 'ಯ', 'ರ', 'ಱ', 'ಲ', 'ಳ', 'ವ', 'ಶ', 'ಷ', 'ಸ', 'ಹ', 'ಕ್ಷ', 'ಜ್ಞ', 'ಾ', 'ಿ', 'ೀ', 'ು', 'ೂ', 'ೃ', 'ೄ', 'ೆ', 'ೇ', 'ೈ', 'ೊ', 'ೋ', 'ೌ', '್', 'ಂ', 'ಃ'],
        "Katakana": ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ', 'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ヤ', 'ユ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ワ', 'ヲ', 'ン', 'ガ', 'ギ', 'グ', 'ゲ', 'ゴ', 'ザ', 'ジ', 'ズ', 'ゼ', 'ゾ', 'ダ', 'ヂ', 'ヅ', 'デ', 'ド', 'バ', 'ビ', 'ブ', 'ベ', 'ボ', 'パ', 'ピ', 'プ', 'ペ', 'ポ', 'キャ', 'キュ', 'キョ', 'シャ', 'シュ', 'ショ', 'チャ', 'チュ', 'チョ', 'ニャ', 'ニュ', 'ニョ', 'ヒャ', 'ヒュ', 'ヒョ', 'ミャ', 'ミュ', 'ミョ', 'リャ', 'リュ', 'リョ', 'ギャ', 'ギュ', 'ギョ', 'ジャ', 'ジュ', 'ジョ', 'ビャ', 'ビュ', 'ビョ', 'ピャ', 'ピュ', 'ピョ', 'ヴ', 'ファ', 'フィ', 'フェ', 'フォ', 'ウィ', 'ウェ', 'ウォ', 'ヵ', 'ヶ', 'ッ'],   
        "Khmer": ['ក', 'ខ', 'គ', 'ឃ', 'ង', 'ច', 'ឆ', 'ជ', 'ឈ', 'ញ', 'ដ', 'ឋ', 'ឌ', 'ឍ', 'ណ', 'ត', 'ថ', 'ទ', 'ធ', 'ន', 'ប', 'ផ', 'ព', 'ភ', 'ម', 'យ', 'រ', 'ល', 'វ', 'ශ', 'ष', 'ស', 'ហ', 'ឡ', 'អ', 'ឥ', 'ឦ', 'ឧ', 'ឨ', 'ឩ', 'ឪ', 'ឫ', 'ឬ', 'ឭ', 'ឮ', 'ឯ', 'ឰ', 'ឱ', 'ឲ', 'ឳ', 'ា', 'ិ', 'ី', 'ឹ', 'ឺ', 'ុ', 'ូ', 'ួ', 'ើ', 'ឿ', 'ៀ', 'េ', 'ែ', 'ៃ', 'ោ', 'ៅ', 'ំ', 'ះ', 'ៈ', '៉', '៊', '់', '៌', '៍', '៎', '៏', '័', '៑', '្', 'ៗ', 'ៜ'],
        "Leton": ['a', 'ā', 'b', 'c', 'č', 'd', 'e', 'ē', 'f', 'g', 'ģ', 'h', 'i', 'ī', 'j', 'k', 'ķ', 'l', 'ļ', 'm', 'n', 'ņ', 'o', 'p', 'r', 's', 'š', 't', 'u', 'ū', 'v', 'z', 'ž'],
        "Lituano": ['a', 'ą', 'b', 'c', 'č', 'd', 'e', 'ę', 'ė', 'f', 'g', 'h', 'i', 'į', 'y', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 'š', 't', 'u', 'ū', 'v', 'z', 'ž'],
        "Polaco": ['a', 'ą', 'b', 'c', 'ć', 'd', 'e', 'ę', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'ł', 'm', 'n', 'ń', 'o', 'ó', 'p', 'r', 's', 'ś', 't', 'u', 'w', 'y', 'z', 'ź', 'ż'],
        "Rumano": [ 'a', 'ă', 'â', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ș', 't', 'ț', 'u', 'v', 'w', 'x', 'y', 'z'],
        "Ruso": ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'],
        "Thai": ['ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ', 'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'เ', 'แ', 'โ', 'ใ', 'ไ', '่', '้', '๊', '๋', '็', '์', 'ํ', 'ฺ'],
        "Tibetano": ['ཀ', 'ཁ', 'ག', 'ང', 'ཅ', 'ཆ', 'ཇ', 'ཉ', 'ཏ', 'ཐ', 'ད', 'ན', 'པ', 'ཕ', 'བ', 'མ', 'ཙ', 'ཚ', 'ཛ', 'ཝ', 'ཞ', 'ཟ', 'འ', 'ཡ', 'ར', 'ལ', 'ཤ', 'ས', 'ཧ', 'ཨ'],
        "Turco": [ 'a', 'b', 'c', 'ç', 'd', 'e', 'f', 'g', 'ğ', 'h', 'ı', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'ö', 'p', 'r', 's', 'ş', 't', 'u', 'ü', 'v', 'y', 'z'],
        "Vietnamita":  ['a', 'ă', 'â', 'b', 'c', 'd', 'đ', 'e', 'ê', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'ô', 'ơ', 'p', 'q', 'r', 's', 't', 'u', 'ư', 'v', 'x', 'y', 'á', 'à', 'ả', 'ã', 'ạ', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'é', 'è', 'ẻ', 'ẽ', 'ẹ', 'ế', 'ề', 'ể', 'ễ', 'ệ', 'í', 'ì', 'ỉ', 'ĩ', 'ị', 'ó', 'ò', 'ỏ', 'õ', 'ọ', 'ố', 'ồ', 'ổ', 'ỗ', 'ộ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ú', 'ù', 'ủ', 'ũ', 'ụ', 'ứ', 'ừ', 'ử', 'ữ', 'ự', 'ý', 'ỳ', 'ỷ', 'ỹ', 'ỵ'],
            "Numeros/signos": {
            "Signos": ['+', '-', '×', '÷', '¡', '!', '¿', '?', '？', ')', '(', '.', '·', '«', '»', ';', ':', '=', '<', '>', '␣'],
            "Amharico": ['፩', '፪', '፫', '፬', '፭', '፮', '፯', '፰', '፱', '፲'],
            "Arabe_clasico": ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩', '؟', '؛'],
            "Arabigos": ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            "Bengali": ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯', '৳', '৺', '৻', 'ঽ', '।', '॥'],
            "Birmano": ['၀', '၁', '၂', '၃', '၄', '၅', '၆', '၇', '၈', '၉', '၊', '။', '၌', '၍', '၎', '၏', '၇', '၈', '၉', '၀', '၏', '္', '့', 'း', '၊', '။', '၍', '၌', '၎', '၏'],
            "Cherokee": ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            "Coreano":  ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '億', '兆', '。', '、', '？', '！', '：', '；', '（', '）', '［', '］', '｛', '｝', '《', '》', '「', '」', '『', '』', '・', '~', '…', '₩'],
            "Devanagari":  ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९', '।', '॥', 'ॐ', '॰', '₹'],
            "Kannada": ['೦', '೧', '೨', '೩', '೪', '೫', '೬', '೭', '೮', '೯', '।', '॥', 'ೱ', 'ೲ', '॰', '₹'],
            "Katakana": ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '。', '、', '！', '？', '：', '；', '（', '）', '「', '」', '『', '』', '・', 'ー', '゛', '゜', '〜', '＿', '￥'],
            "Khmer": ['០', '១', '២', '៣', '៤', '៥', '៦', '៧', '៨', '៩', '។', '៕', '៖', '៘', '៙', '៚', '៛', '៝', '៞', '៟', '៰', '៱', '៲', '៳', '៴', '៵', '៶', '៷', '៸', '៹'],
            "Thai": ['๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙', '฿', '๏', 'ๆ', '฿', '฿', '๚', '๛', '๏', '๚', '๛', '๎', '๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙', '๚', '๛', '๏', '๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙'],
                }
            }
        self.configurar_estilos()
        self.medida_plantilla = ttk.Combobox(self, font=("TkDefaultFont", self.medida_fuente))
        self.medida_plantilla.set(self.traducciones[self.idioma_actual]["(2, 56)"])
        self.actualizar_idioma()
        
    def crear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
    
        self.widgets_traducibles = []
    
        # Crear un frame principal
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
        # Configurar el grid del frame principal
        for i in range(4):
            main_frame.grid_columnconfigure(i, weight=1)
        for i in range(9):
            main_frame.grid_rowconfigure(i, weight=1)
    
        # Título de la ventana
        self.title(self.traducciones[self.idioma_actual].get("titulo", ""))
    
        # Radiobuttons y botón de gestionar
        rb_cifrar = ttk.Radiobutton(main_frame, text=self.traducciones[self.idioma_actual].get("cifrar_texto", ""), 
                    variable=self.opcion, value="cifrar")
        rb_cifrar.grid(row=0, column=0, sticky="w")
        self.widgets_traducibles.append((rb_cifrar, "cifrar_texto"))
    
        rb_descifrar = ttk.Radiobutton(main_frame, text=self.traducciones[self.idioma_actual].get("descifrar_texto", ""), 
                        variable=self.opcion, value="descifrar")
        rb_descifrar.grid(row=0, column=1, sticky="w")
        self.widgets_traducibles.append((rb_descifrar, "descifrar_texto"))

        btn_file_encryption = ttk.Button(main_frame, text=self.traducciones[self.idioma_actual].get("file_encryption", ""), 
                                          command=self.abrir_ventana_cifrado_archivos)
        btn_file_encryption.grid(row=0, column=3, sticky="w")
        self.widgets_traducibles.append((btn_file_encryption, "file_encryption"))
    
        btn_gestionar = ttk.Button(main_frame, text=self.traducciones[self.idioma_actual].get("gestionar_plantillas", ""), 
                   command=self.gestionar_plantillas)
        btn_gestionar.grid(row=0, column=2, sticky="w")
        self.widgets_traducibles.append((btn_gestionar, "gestionar_plantillas"))
    
        # Botón de ajustes
        icono_pil = self.crear_icono()
        icono_tk = ImageTk.PhotoImage(icono_pil)
        self.boton_ajustes = ttk.Button(main_frame, image=icono_tk, command=self.mostrar_menu_ajustes)
        self.boton_ajustes.image = icono_tk
        self.boton_ajustes.grid(row=0, column=4, sticky="e")
    
        # Texto
        lbl_texto = ttk.Label(main_frame, text=self.traducciones[self.idioma_actual].get("texto", ""))
        lbl_texto.grid(row=1, column=0, sticky="w")
        self.widgets_traducibles.append((lbl_texto, "texto"))
    
        self.texto = tk.Text(main_frame, height=10, width=50, wrap=tk.WORD)
        self.texto.grid(row=1, column=1, columnspan=3, sticky="nsew")
        self.texto.bind("<Control-c>", self.copy_text)
        self.texto.bind("<Control-x>", self.cut_text)
        self.texto.bind("<Control-v>", self.paste_text)
        self.texto.bind("<Control-a>", self.select_all)
        self.texto.configure(selectbackground="lightblue", selectforeground="black")
        
        # Valores
        for i in range(4):
            lbl_valor = ttk.Label(main_frame, text=f"Valor {i+1}:")
            lbl_valor.grid(row=i+2, column=0, sticky="w")
            self.widgets_traducibles.append((lbl_valor, f"valor_{i+1}"))
            setattr(self, f"valor{i+1}", ttk.Entry(main_frame, width=10))
            getattr(self, f"valor{i+1}").grid(row=i+2, column=1, sticky="ew")
    
        # Plantilla
        lbl_plantilla = ttk.Label(main_frame, text=self.traducciones[self.idioma_actual].get("seleccionar_plantilla", ""))
        lbl_plantilla.grid(row=6, column=0, sticky="w")
        self.widgets_traducibles.append((lbl_plantilla, "seleccionar_plantilla"))
        
        # Inicializa el Combobox para plantillas
        self.plantilla = ttk.Combobox(main_frame, font=("TkDefaultFont", self.medida_fuente))  
        self.plantilla.grid(row=6, column=1, columnspan=3, sticky="ew")
        
        # Bind para manejar la selección
        self.plantilla.bind("<<ComboboxSelected>>", self.actualizar_seleccion_plantilla)

        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=4, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
    
        btn_ejecutar = ttk.Button(btn_frame, text=self.traducciones[self.idioma_actual].get("ejecutar", ""), command=self.ejecutar)
        btn_ejecutar.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="ew")
        self.widgets_traducibles.append((btn_ejecutar, "ejecutar"))
    
        btn_limpiar = ttk.Button(btn_frame, text=self.traducciones[self.idioma_actual].get("limpiar", ""), command=self.limpiar)
        btn_limpiar.grid(row=0, column=1, padx=10, pady=(20, 10), sticky="ew")
        self.widgets_traducibles.append((btn_limpiar, "limpiar"))
    
        btn_salir = ttk.Button(btn_frame, text=self.traducciones[self.idioma_actual].get("salir", ""), command=self.quit)
        btn_salir.grid(row=0, column=2, padx=10, pady=(20, 10), sticky="ew")
        self.widgets_traducibles.append((btn_salir, "salir"))

        # Resultado
        self.resultado = tk.Text(main_frame, height=10, width=50)
        self.resultado.grid(row=8, column=0, columnspan=4, sticky="nsew")
        self.resultado.bind("<Control-c>", self.copy_text)
        self.resultado.bind("<Control-x>", self.cut_text)
        self.resultado.bind("<Control-v>", self.paste_text)
        self.resultado.bind("<Control-a>", self.select_all)
        self.resultado.configure(selectbackground="lightblue", selectforeground="black")
        
        self.actualizar_lista_plantillas()

    def abrir_ventana_cifrado_archivos(self):
        ventana = tk.Toplevel(self)
        ventana.title(self.traducciones[self.idioma_actual]["file_encryption"])
        ventana.geometry("500x700")

        main_frame = ttk.Frame(ventana)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Radiobuttons para cifrar y descifrar
        rb_cifrar = ttk.Radiobutton(main_frame, text=self.traducciones[self.idioma_actual]["cifrar"], 
                                     variable=self.opcion, value="cifrar")
        rb_cifrar.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        rb_descifrar = ttk.Radiobutton(main_frame, text=self.traducciones[self.idioma_actual]["descifrar"], 
                                       variable=self.opcion, value="descifrar")
        rb_descifrar.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Botón de cargar (en fila 1)
        ttk.Button(main_frame, text=self.traducciones[self.idioma_actual]["cargar_fichero"], 
                   command=lambda: self.cargar_archivo(ventana)).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Campos de entrada (comenzando en fila 2)
        for i in range(1, 6):
            clave_traduccion = f"valor_{i}"
            lbl_valor = ttk.Label(main_frame, text=f"{self.traducciones[self.idioma_actual].get(clave_traduccion, f'Value {i}')}")
            lbl_valor.grid(row=i + 1, column=0, sticky="w", padx=5, pady=5)  # Fila i + 1
        
            entry = ttk.Entry(main_frame, width=10)
            entry.grid(row=i + 1, column=1, sticky="we", padx=5, pady=5)  # Fila i + 1
            
            # Asignar a ventana en lugar de main_frame
            setattr(ventana, f'valor{i}', entry)
        
        # Texto de información (en fila 7)
        ventana.info = tk.Text(main_frame, height=17, width=50)
        ventana.info.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Frame de botones (en fila 8)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Botones dentro del frame
        ttk.Button(button_frame, text=self.traducciones[self.idioma_actual]["ejecutar"], 
                   command=lambda: self.ejecutar_cifrado_archivos(self.opcion.get(), ventana)).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text=self.traducciones[self.idioma_actual]["limpiar"], 
                   command=lambda: self.limpiar_ventana_cifrado(ventana)).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text=self.traducciones[self.idioma_actual]["guardar"], 
                   command=lambda: self.guardar_resultado(ventana)).pack(side=tk.LEFT, padx=10)

    def cargar_archivo(self, ventana):
        filename = filedialog.askopenfilename(parent=ventana, title=self.traducciones[self.idioma_actual]["seleccionar_fichero"])
        if filename:
            self.original_filename = os.path.basename(filename)
            
            # Obtener el tamaño del archivo original
            original_size = os.path.getsize(filename)
            
            opcion = self.preguntar_cifrar_descifrar()
            if opcion == "cifrar":
                self.procesar_cifrado(filename, ventana, original_size)
            elif opcion == "descifrar":
                self.procesar_descifrado(filename, ventana)  # Removed original_size argument

    def preguntar_cifrar_descifrar(self):
        ventana_pregunta = tk.Toplevel(self)
        ventana_pregunta.title(self.traducciones[self.idioma_actual]["titulo_cifrar_descifrar"])
        ventana_pregunta.geometry("300x150")
      
        opcion = tk.StringVar()
        
        frame = tk.Frame(ventana_pregunta)
        frame.pack(expand=True)
        
        tk.Radiobutton(frame, text=self.traducciones[self.idioma_actual]["opcion_cifrar"], variable=opcion, value="cifrar", font=("TkDefaultFont", 13)).pack(side=tk.LEFT, padx=20)
        tk.Radiobutton(frame, text=self.traducciones[self.idioma_actual]["opcion_descifrar"], variable=opcion, value="descifrar", font=("TkDefaultFont", 13)).pack(side=tk.LEFT, padx=20)
        
        tk.Button(ventana_pregunta, text=self.traducciones[self.idioma_actual]["boton_aceptar"], command=ventana_pregunta.quit, font=("TkDefaultFont", 13)).pack(pady=20)
        
        ventana_pregunta.mainloop()
        resultado = opcion.get()
        ventana_pregunta.destroy()
        return resultado

    def procesar_cifrado(self, filename, ventana, original_size):
        try:
            if filename.lower().endswith('.txt'):
                with open(filename, 'rb') as file:
                    content = file.read()
                
                # Comprimir el contenido
                compressed_content = self.comprimir_archivo(content)
                
                # Convertir a hexadecimal
                hex_content = compressed_content.hex()
            else:
                with open(filename, 'rb') as file:
                    content = file.read()
                hex_content = content.hex()
            
            temp_file = os.path.join(self.directorio_plantillas, "temp_file.txt")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(hex_content)
            
            self.total_chars = len(hex_content)
            ventana.info.insert(tk.END, f"{self.original_filename}\n")
            ventana.info.insert(tk.END, f"{self.traducciones[self.idioma_actual]['total_caracteres_original']}: {len(content)}\n")
            ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["convertido_a_hexadecimal"] + "\n")
            ventana.info.insert(tk.END, f"{self.traducciones[self.idioma_actual]['total_caracteres_hexadecimal']}: {self.total_chars}\n")
            ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["archivo_temporal_creado"] + "\n")
        
        except Exception as e:
            messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                 f"{self.traducciones[self.idioma_actual]['no_cargar_archivo']}: {str(e)}", 
                                 parent=ventana)

    def procesar_descifrado(self, filename, ventana):
        ventana_referencia = tk.Toplevel(self)
        ventana_referencia.title(self.traducciones[self.idioma_actual]["insertar_referencia_titulo"])
        ventana_referencia.geometry("300x150")
        
        entrada = tk.Entry(ventana_referencia, width=50)
        entrada.pack()
        
        def procesar():
            referencia = entrada.get()
            ventana_referencia.destroy()
            self.buscar_y_eliminar_referencia(filename, referencia, ventana)
        
        tk.Button(ventana_referencia, text=self.traducciones[self.idioma_actual]["boton_aceptar"], command=procesar).pack()
        
        ventana_referencia.mainloop()

    def buscar_y_eliminar_referencia(self, filename, referencia, ventana):
        temp_file = os.path.join(self.directorio_plantillas, "temp_file.txt")
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if referencia in content:
                nuevo_contenido = content.replace(referencia, '', 1)
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(nuevo_contenido)
                ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["referencia_encontrada_eliminada"] + "\n")
            else:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["referencia_no_encontrada"] + "\n")
            
            self.total_chars = len(content)
            ventana.info.insert(tk.END, f"{self.traducciones[self.idioma_actual]['total_caracteres']}: {self.total_chars}\n{self.traducciones[self.idioma_actual]['archivo_temporal_creado']}\n")
        
        except Exception as e:
            messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                 f"{self.traducciones[self.idioma_actual]['no_procesar_archivo']}: {str(e)}", 
                                 parent=ventana)

    def comprimir_archivo(self, content):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('compressed_file', content)
        return buffer.getvalue()

    def ejecutar_cifrado_archivos(self, modo, ventana):
        try:
            caja_values = [int(getattr(ventana, f'valor{i}').get()) for i in range(1, 6)]
            if any(value == '' for value in caja_values):
                raise ValueError(self.traducciones[self.idioma_actual]["cajas_vacias"])
        except ValueError as e:
            messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                 self.traducciones[self.idioma_actual]["ingrese_numeros"], 
                                 parent=ventana)
            return
    
        temp_file = os.path.join(self.directorio_plantillas, "temp_file.txt")
        if not os.path.exists(temp_file):
            messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                 self.traducciones[self.idioma_actual]["nocontenido"], 
                                 parent=ventana)
            return
    
        with open(temp_file, 'r') as f:
            content = f.read()
    
        if modo == "cifrar":
            resultado = self.cifrar_archivo(content, *caja_values)
            ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["cifrado_realizado"] + "\n")
            ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["cifrado_guardado"] + "\n")
            ventana.info.insert(tk.END, f"{self.traducciones[self.idioma_actual]['contenido_guardado']}: {len(resultado)} {self.traducciones[self.idioma_actual]['caracteres']}\n")
        else:
            resultado = self.descifrar_archivo(content, *caja_values)
            ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["descifrado_realizado"] + "\n")
            ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["descifrado_guardado"] + "\n")
            ventana.info.insert(tk.END, f"{self.traducciones[self.idioma_actual]['tamano_archivo']}: {len(resultado)} {self.traducciones[self.idioma_actual]['bytes']}\n")
    
        with open(temp_file, 'w') as f:
            f.write(resultado)
        
        ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["archivo_temporal_eliminado"] + "\n")

    def procesar_texto_archivo(self, texto_hex, caja1, caja2, caja3, caja4, caja5, modo):
        teclado = self.teclados["filelivencrypt"]["layout"]
        resultado = ''
        total_chars = len(texto_hex)
    
        def encontrar_posicion(caracter):
            for i, fila in enumerate(teclado):
                if caracter.lower() in [c.lower() for c in fila]:
                    return i, [c.lower() for c in fila].index(caracter.lower())
            return None, None
    
        def obtener_movimientos_caja5(indice, caja5, total_chars):
            if caja5 == total_chars - 1:
                return []
            
            secuencia = indice % 2
            movimientos = []
            if secuencia == 1:
                parte = caja5 % 4
                if parte == 0:
                    movimientos.extend([(2, 0), (0, 1)])
                elif parte == 1:
                    movimientos.extend([(0, 2), (1, 0)])
                elif parte == 2:
                    movimientos.extend([(-2, 0), (0, -1)])
                else:
                    movimientos.extend([(0, -2), (-1, 0)])
            return movimientos
    
        for i, caracter in enumerate(texto_hex):
            fila, columna = encontrar_posicion(caracter)
            
            if fila is not None and columna is not None:
                indice = total_chars - i if modo == "cifrar" else i + 1
    
                # Aplicamos las transformaciones usando las cajas 1-4
                if modo == "cifrar":
                    columna = (columna + int(caja1) - indice) % len(teclado[0])
                    fila = (fila + int(caja2) - indice) % len(teclado)
                    columna = (columna - int(caja3) + indice) % len(teclado[0])
                    fila = (fila - int(caja4) + indice) % len(teclado)
                else:  # descifrar
                    fila = (fila + int(caja4) - indice) % len(teclado)
                    columna = (columna + int(caja3) - indice) % len(teclado[0])
                    fila = (fila - int(caja2) + indice) % len(teclado)
                    columna = (columna - int(caja1) + indice) % len(teclado[0])
    
                # Aplicamos los movimientos de la caja 5
                movimientos_caja5 = obtener_movimientos_caja5(i, int(caja5), total_chars)
                for mov_fila, mov_columna in movimientos_caja5:
                    if modo == "cifrar":
                        fila = (fila + mov_fila) % len(teclado)
                        columna = (columna + mov_columna) % len(teclado[0])
                    else:  # descifrar
                        fila = (fila - mov_fila) % len(teclado)
                        columna = (columna - mov_columna) % len(teclado[0])
    
                nuevo_caracter = teclado[fila][columna]
                resultado += nuevo_caracter
    
        return resultado

    def cifrar_archivo(self, texto_hex, caja1, caja2, caja3, caja4, caja5):
        return self.procesar_texto_archivo(texto_hex, caja1, caja2, caja3, caja4, caja5, "cifrar")
    
    def descifrar_archivo(self, texto_hex, caja1, caja2, caja3, caja4, caja5):
        return self.procesar_texto_archivo(texto_hex, caja1, caja2, caja3, caja4, caja5, "descifrar")
            
    def guardar_resultado(self, ventana):
        temp_file = os.path.join(self.directorio_plantillas, "temp_file.txt")
        if not os.path.exists(temp_file):
            messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                 self.traducciones[self.idioma_actual]["noguardar"], 
                                 parent=ventana)
            return
    
        base_filename = os.path.splitext(self.original_filename)[0]
    
        if self.opcion.get() == "cifrar":
            default_filename = f"{base_filename}_{self.traducciones[self.idioma_actual]['cifrado']}.txt"
            filetypes = [("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")]
        else:
            extension = simpledialog.askstring(self.traducciones[self.idioma_actual]["extension_titulo"], 
                                               self.traducciones[self.idioma_actual]["extension_mensaje"],
                                               parent=ventana)
            if extension is None:
                return
            if not extension.startswith('.'):
                extension = '.' + extension
            default_filename = f"{base_filename}_{self.traducciones[self.idioma_actual]['descifrado']}{extension}"
            filetypes = [("Todos los archivos", "*.*")]
    
        initial_dir = self.directorio_plantillas
        save_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            initialfile=default_filename,
            filetypes=filetypes,
            parent=ventana
        )
    
        if save_path:
            # Leer el contenido temporal
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
    
            # Eliminar espacios y saltos de línea en el contenido leído
            content_limpio = content.replace(' ', '').replace('\n', '')
    
            if self.opcion.get() == "cifrar":
                referencia = self.solicitar_referencia(ventana)
                if referencia:
                    content_con_referencia = self.insertar_referencia_aleatoria(content_limpio, referencia)
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(content_con_referencia)
                    ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["cifrado_guardado"] + "\n")
                    ventana.info.insert(tk.END, f"{self.traducciones[self.idioma_actual]['contenido_guardado']}: {len(content_con_referencia)} {self.traducciones[self.idioma_actual]['caracteres']}\n")
            else:
                try:
                    # Convertir de hexadecimal a binario
                    binary_content = bytes.fromhex(content_limpio)
                    
                    if extension == '.txt':
                        # Descomprimir el contenido
                        decompressed_content = self.descomprimir_archivo(binary_content)
                        
                        # Guardar el contenido descomprimido como archivo de texto
                        with open(save_path, 'wb') as f:
                            f.write(decompressed_content)
                    else:
                        # Para otros formatos, guardar directamente el contenido binario
                        with open(save_path, 'wb') as f:
                            f.write(binary_content)
                    
                    ventana.info.insert(tk.END, f"{self.traducciones[self.idioma_actual]['descifrado_guardado_original']} \n")
                    ventana.info.insert(tk.END, f"{self.traducciones[self.idioma_actual]['tamano_archivo']}: {len(binary_content)} {self.traducciones[self.idioma_actual]['bytes']}\n")
                except ValueError as e:
                    messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                         f"{self.traducciones[self.idioma_actual]['hex_invalido']}: {str(e)}", 
                                         parent=ventana)
                    return
    
            messagebox.showinfo(self.traducciones[self.idioma_actual]["exito"], 
                                self.traducciones[self.idioma_actual]["archivo_guardado"], 
                                parent=ventana)
    
        # Limpiar fichero temporal
        if os.path.exists(temp_file):
            os.remove(temp_file)
        ventana.info.insert(tk.END, self.traducciones[self.idioma_actual]["archivo_temporal_eliminado"] + "\n")

    def descomprimir_archivo(self, compressed_content):
        try:
            zip_buffer = io.BytesIO(compressed_content)
            with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                # Asumimos que solo hay un archivo en el ZIP
                file_name = zip_file.namelist()[0]
                return zip_file.read(file_name)
        except zipfile.BadZipFile:
            # Si el contenido no es un ZIP válido, devolvemos el contenido original
            return compressed_content

    def solicitar_referencia(self, ventana):
        while True:
            referencia = simpledialog.askstring(self.traducciones[self.idioma_actual]["insertar_referencia_titulo"], 
                                                self.traducciones[self.idioma_actual]["insertar_referencia_mensaje"],
                                                parent=ventana)
            if referencia is None:
                return None
            if ' ' in referencia:
                messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                     self.traducciones[self.idioma_actual]["referencia_espacios"], 
                                     parent=ventana)
            else:
                return referencia


    def insertar_referencia_aleatoria(self, content, referencia):
        posicion = random.randint(0, len(content))
        return content[:posicion] + referencia + content[posicion:]

    def limpiar_ventana_cifrado(self, ventana):
        for i in range(1, 6):
            # Cambiamos 'caja' por 'valor' para limpiar las entradas correctas
            getattr(ventana, f'valor{i}').delete(0, tk.END)
        ventana.info.delete(1.0, tk.END)
        temp_file = os.path.join(self.directorio_plantillas, "temp_file.txt")
        if os.path.exists(temp_file):
            os.remove(temp_file)

    def select_all(self, event):
        event.widget.tag_add('sel', '1.0', 'end')
        return 'break'
    
    def copy_text(self, event):
        if event.widget.tag_ranges('sel'):
            event.widget.clipboard_clear()
            event.widget.clipboard_append(event.widget.selection_get())
        return 'break'
    
    def cut_text(self, event):
        if event.widget.tag_ranges('sel'):
            event.widget.clipboard_clear()
            event.widget.clipboard_append(event.widget.selection_get())
            event.widget.delete('sel.first', 'sel.last')
        return 'break'
    
    def paste_text(self, event):
        try:
            texto_pegado = event.widget.clipboard_get()
            caracteres_pegados = [c.strip() for c in texto_pegado.split(',') if c.strip()]
            
            widget = event.widget
    
            # Si el widget pertenece a los creados en crear_widgets, se pega tal cual
            if widget in self.winfo_children():
                try:
                    start_index = widget.index(tk.SEL_FIRST)
                    end_index = widget.index(tk.SEL_LAST)
    
                    # Reemplaza el texto seleccionado con el texto pegado
                    widget.delete(start_index, end_index)
                except tk.TclError:
                    # Si no hay texto seleccionado, usa la posición actual del cursor
                    start_index = widget.index(tk.INSERT)
    
                # Pega el texto tal cual, sin modificaciones
                widget.insert(start_index, texto_pegado)
            else:
                # Verifica si es la caja de crear_plantilla
                if hasattr(self, 'plantilla_texto') and widget == self.plantilla_texto:
                    contenido_actual = widget.get("1.0", tk.END).strip()
                    caracteres_actuales = set(c.strip() for c in contenido_actual.split(',') if c.strip())
    
                    # Elimina los caracteres repetidos
                    caracteres_nuevos = [c for c in caracteres_pegados if c not in caracteres_actuales]
    
                    if not caracteres_nuevos:
                        # Si no hay caracteres nuevos, no hace nada
                        return "break"
    
                    # Pega solo los caracteres nuevos
                    if contenido_actual:
                        nuevo_contenido = contenido_actual + ', ' + ', '.join(caracteres_nuevos)
                    else:
                        nuevo_contenido = ', '.join(caracteres_nuevos)
    
                    widget.delete("1.0", tk.END)
                    widget.insert(tk.END, nuevo_contenido)
                else:
                    # Para otros widgets (fuera de los de crear_widgets)
                    try:
                        start_index = widget.index(tk.SEL_FIRST)
                        end_index = widget.index(tk.SEL_LAST)
    
                        # Reemplaza el texto seleccionado con el texto pegado
                        widget.delete(start_index, end_index)
                    except tk.TclError:
                        # Si no hay texto seleccionado, usa la posición actual del cursor
                        start_index = widget.index(tk.INSERT)
    
                    # Inserta el texto pegado una sola vez
                    widget.insert(start_index, ', '.join(caracteres_pegados))
    
        except tk.TclError:
            pass  # No hay nada en el portapapeles
    
        return "break"

        
    def actualizar_seleccion_plantilla(self, event=None):
        seleccion = self.plantilla.get()
        # Buscar la clave original basada en la selección traducida
        for key in self.teclados.keys():
            if self.traducciones[self.idioma_actual].get(key, key) == seleccion:
                self.plantilla_seleccionada = key
                break
        else:
            # Si no se encuentra en las plantillas predefinidas, es una plantilla personalizada
            self.plantilla_seleccionada = seleccion

    def mostrar_menu_ajustes(self):
        # Asegúrate de que este método se llame solo al hacer clic en el botón de ajustes
        menu_ajustes = tk.Menu(self, tearoff=0, font=("TkDefaultFont", self.medida_fuente))
        menu_ajustes.add_command(label=self.traducciones[self.idioma_actual]["cambiar_idioma"], command=self.cambiar_idioma)
        menu_ajustes.add_command(label=self.traducciones[self.idioma_actual]["cambiar_tamano_letra"], command=self.cambiar_tamano_letra)
        menu_ajustes.add_command(label=self.traducciones[self.idioma_actual]["faq"], command=self.faq)
        menu_ajustes.add_command(label=self.traducciones[self.idioma_actual]["consejos"], command=self.mostrar_consejos)
        menu_ajustes.add_command(label=self.traducciones[self.idioma_actual]["creditos"], command=self.mostrar_creditos)
        menu_ajustes.add_command(label=self.traducciones[self.idioma_actual]["licencia"], command=self.licencia)
        
        # Mostrar el menú en la posición del botón
        x = self.boton_ajustes.winfo_rootx()
        y = self.boton_ajustes.winfo_rooty() + self.boton_ajustes.winfo_height()
        menu_ajustes.tk_popup(x, y)
    
    def cambiar_idioma(self):
        idiomas = list(self.traducciones.keys())
        nuevo_idioma = tk.StringVar(value=self.idioma_actual)
        
        dialog = tk.Toplevel(self)
        dialog.title(self.traducciones[self.idioma_actual]["cambiar_idioma"])
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text=self.traducciones[self.idioma_actual].get("seleccionar_idioma", "Seleccione un idioma:")).pack(padx=10, pady=10)
        
        option_menu = ttk.OptionMenu(dialog, nuevo_idioma, self.idioma_actual, *idiomas)
        option_menu.pack(padx=10, pady=10)
    
        def on_accept():
            self.idioma_actual = nuevo_idioma.get()
            self.actualizar_idioma()
            dialog.destroy()
    
        ttk.Button(dialog, text=self.traducciones[self.idioma_actual].get("aceptar", "Aceptar"), command=on_accept).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(dialog, text=self.traducciones[self.idioma_actual].get("cancelar", "Cancelar"), command=dialog.destroy).pack(side=tk.RIGHT, padx=10, pady=10)
        
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        self.wait_window(dialog)

    def actualizar_idioma(self):
        plantillas_personalizadas_temp = self.plantillas_personalizadas.copy()

        self.title(self.traducciones[self.idioma_actual].get("titulo", ""))
        self.actualizar_widgets_traducibles()
        self.actualizar_lista_plantillas()
        self.plantillas_personalizadas = plantillas_personalizadas_temp

        medidas_plantilla = [
            self.traducciones[self.idioma_actual]["(2, 56)"],
            self.traducciones[self.idioma_actual]["(4, 28)"],
            self.traducciones[self.idioma_actual]["(7, 16)"],
            self.traducciones[self.idioma_actual]["(8, 14)"],
            self.traducciones[self.idioma_actual]["(14, 8)"],
            self.traducciones[self.idioma_actual]["(16, 7)"],
            self.traducciones[self.idioma_actual]["(28, 4)"],
            self.traducciones[self.idioma_actual]["(3, 56)"],
            self.traducciones[self.idioma_actual]["(4, 56)"],
            self.traducciones[self.idioma_actual]["(5, 56)"],
            self.traducciones[self.idioma_actual]["(7, 56)"],
            self.traducciones[self.idioma_actual]["(8, 56)"],
            self.traducciones[self.idioma_actual]["(10, 56)"],
            self.traducciones[self.idioma_actual]["(11, 56)"],
            self.traducciones[self.idioma_actual]["(14, 56)"],
        ]
    
        if hasattr(self, 'medida_plantilla') and self.medida_plantilla.winfo_exists():
            medidas_plantilla = [self.traducciones[self.idioma_actual].get(key, key) for key in self.medidas_plantilla.keys()]
            self.medida_plantilla['values'] = medidas_plantilla
    
            # Actualizar la selección actual si existe
            if self.medida_plantilla.get():
                for clave in self.medidas_plantilla.keys():
                    if self.traducciones[self.idioma_actual][clave] == self.medida_plantilla.get():
                        self.medida_plantilla.set(self.traducciones[self.idioma_actual][clave])
                        break
        
        self.update_idletasks()

    def obtener_medida_numerica(self, medida_str):
        try:
            # Eliminar los paréntesis y dividir por la coma
            numeros = medida_str.strip('()').split(',')
            return (int(numeros[0].strip()), int(numeros[1].strip()))
        except:
            return (2, 56)  # valor por defecto si no se puede parsear
    
    def actualizar_widgets_traducibles(self):
        for widget, clave in self.widgets_traducibles:
            try:
                if widget.winfo_exists():
                    if isinstance(widget, (ttk.Radiobutton, ttk.Button, ttk.Label)):
                        widget.config(text=self.traducciones[self.idioma_actual].get(clave, clave))
            except tk.TclError:
                # El widget ya no existe, lo eliminamos de la lista
                self.widgets_traducibles.remove((widget, clave))
        
        # Actualizar los checkbuttons de idiomas si existen
        if hasattr(self, 'idiomas_var'):
            for idioma, (var, checkbutton) in list(self.idiomas_var.items()):
                try:
                    if checkbutton.winfo_exists():
                        text = self.traducciones[self.idioma_actual].get(idioma, idioma)
                        checkbutton.config(text=text)
                except tk.TclError:
                    # El checkbutton ya no existe, lo eliminamos del diccionario
                    del self.idiomas_var[idioma]

    def actualizar_widgets_por_tipo(self):
        for widget, key in self.widgets_traducibles:
            if isinstance(widget, (ttk.Radiobutton, ttk.Button, ttk.Label)):
                widget.config(text=self.traducciones[self.idioma_actual].get(key, ""))
    
    def actualizar_labels_valores(self):
        for i in range(4):
            label_key = f"valor_{i+1}"
            label_text = self.traducciones[self.idioma_actual].get(label_key, f"Valor {i+1}:")
            for widget, key in self.widgets_traducibles:
                if key == label_key:
                    widget.config(text=label_text)
                    break
    
    def actualizar_combobox_plantillas(self):
        plantillas_traducidas = [self.traducciones[self.idioma_actual].get(k, k) for k in self.teclados.keys()]
        self.plantilla['values'] = plantillas_traducidas + list(self.plantillas_personalizadas.keys())
        if self.plantilla.get() in self.teclados:
            self.plantilla.set(self.traducciones[self.idioma_actual].get(self.plantilla.get(), self.plantilla.get()))
        
    def actualizar_lista_plantillas(self):
        if not hasattr(self, 'teclados') or not hasattr(self, 'traducciones') or not hasattr(self, 'idioma_actual'):
            return
    
        try:
            # Combina plantillas predefinidas y personalizadas, traduciendo los nombres
            plantillas_traducidas = [self.traducciones[self.idioma_actual].get(key, key) for key in self.teclados.keys()]
            todas_las_plantillas = plantillas_traducidas + list(self.plantillas_personalizadas.keys())
    
            # Crea un diccionario de correspondencia entre nombres traducidos y originales
            self.correspondencia_plantillas = {self.traducciones[self.idioma_actual].get(key, key): key for key in self.teclados.keys()}
            self.correspondencia_plantillas.update({key: key for key in self.plantillas_personalizadas.keys()})
    
            # Actualiza el combobox con todas las plantillas disponibles
            self.plantilla['values'] = todas_las_plantillas
    
            # Restablece la plantilla seleccionada a vacío si la actual no está en la lista de plantillas
            seleccionada = self.plantilla.get()
            if seleccionada not in todas_las_plantillas:
                self.plantilla.set("")
            else:
                # Actualiza la selección con el nombre traducido
                self.plantilla.set(seleccionada)
    
        except Exception as e:
            pass  # O puedes manejar el error de manera diferente si lo prefieres
            
    def obtener_layout_plantilla(self, nombre_plantilla):
        # Obtiene el nombre original de la plantilla
        nombre_original = self.correspondencia_plantillas.get(nombre_plantilla, nombre_plantilla)
        
        if nombre_original in self.teclados:
            return self.teclados[nombre_original]['layout']
        elif nombre_original in self.plantillas_personalizadas:
            return self.plantillas_personalizadas[nombre_original]
        return None
    
    def crear_icono(self):
        # Crear una imagen PIL con fondo transparente
        icono = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icono)

        # Dibujar un círculo
        draw.ellipse((8, 8, 40, 40), outline="black")
        draw.ellipse((4, 4, 36, 36), outline="black")
        
        # Dibujar las líneas cruzadas
        draw.line((3, 6, 9, 8), fill="black")
        draw.line((10, 5, 8, 8), fill="black")
        draw.line((8, 2, 8, 6), fill="black")
        draw.line((14, 4, 7, 9), fill="black")
        draw.line((20, 3, 7, 6), fill="black")
        draw.line((10, 4, 5, 4), fill="black")
        draw.line((3, 4, 5, 2), fill="black")

        return icono

    def gestionar_plantillas(self):
        self.ventana_gestion = tk.Toplevel(self)
        self.ventana_gestion.title(self.traducciones[self.idioma_actual]["gestionar_plantillas"])
        self.ventana_gestion.geometry("300x150")
        
        ttk.Button(self.ventana_gestion, text=self.traducciones[self.idioma_actual]["crear_plantilla"], 
                   command=self.crear_plantilla_y_cerrar).pack(pady=10)
        ttk.Button(self.ventana_gestion, text=self.traducciones[self.idioma_actual]["editar_plantilla"], 
                   command=self.editar_plantilla_y_cerrar).pack(pady=10)
        
        # Centrar la ventana
        self.ventana_gestion.update_idletasks()
        width = self.ventana_gestion.winfo_width()
        height = self.ventana_gestion.winfo_height()
        x = (self.ventana_gestion.winfo_screenwidth() // 2) - (width // 2)
        y = (self.ventana_gestion.winfo_screenheight() // 2) - (height // 2)
        self.ventana_gestion.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        self.ventana_gestion.focus_set()
    
    def crear_plantilla_y_cerrar(self):
        self.crear_plantilla()
        self.ventana_gestion.destroy()
    
    def editar_plantilla_y_cerrar(self):
        self.editar_plantilla()
        self.ventana_gestion.destroy()

    def crear_plantilla(self):
        ventana_crear = tk.Toplevel(self)
        ventana_crear.title(self.traducciones[self.idioma_actual]["crear_plantilla"])
    
        # Obtener dimensiones de la pantalla
        ancho_pantalla = ventana_crear.winfo_screenwidth()
        alto_pantalla = ventana_crear.winfo_screenheight()
    
        # Calcular dimensiones de la ventana (100% del tamaño de la pantalla)
        ancho_ventana = ancho_pantalla
        alto_ventana = alto_pantalla
    
        # Configurar geometría de la ventana
        ventana_crear.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")
    
        # Frame principal con grid
        main_frame = ttk.Frame(ventana_crear)
        main_frame.grid(row=0, column=0, sticky="nsew")
    
        ventana_crear.grid_rowconfigure(0, weight=1)
        ventana_crear.grid_columnconfigure(0, weight=1)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Actualizar el tamaño del canvas cuando cambia el tamaño del contenido
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Asegurarse de que el canvas y el scrollbar se ajusten al tamaño del frame
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel events
        self.bind_scroll_events(canvas)
    
        # Estilo para los widgets
        estilo = ttk.Style()
        estilo.configure("TCheckbutton", font=("TkDefaultFont", self.medida_fuente))
        estilo.configure("TLabel", font=("TkDefaultFont", self.medida_fuente))
        estilo.configure("TButton", font=("TkDefaultFont", self.medida_fuente))
    
        # Menú desplegable de idiomas
        ttk.Label(scrollable_frame, text=self.traducciones[self.idioma_actual]["seleccione_idiomas"]).pack(pady=10)
        self.idiomas_var = {}
        self.idiomas_frame = ttk.Frame(scrollable_frame)
        self.idiomas_frame.pack(pady=10, fill='x')
    
        idiomas = list(self.caracteres_por_idioma.keys())
        for i, idioma in enumerate(idiomas):
            row = i // 9
            col = i % 9
            var = tk.BooleanVar()
            self.idiomas_var[idioma] = var
            
            text = self.traducciones[self.idioma_actual].get(idioma, idioma)
            
            checkbutton = ttk.Checkbutton(self.idiomas_frame, text=text, variable=var, command=self.actualizar_caracteres)
            checkbutton.grid(row=row, column=col, sticky="w", padx=5, pady=2)
            
            self.idiomas_var[idioma] = (var, checkbutton)
    
        # Asegurar el número de columnas en la última fila para mantener la alineación
        for i in range(len(idiomas), 45):
            row = i // 9
            col = i % 9
            ttk.Label(self.idiomas_frame, text="").grid(row=row, column=col, sticky="w", padx=5, pady=2)
    
        # Frame para mostrar los caracteres
        ttk.Label(scrollable_frame, text=self.traducciones[self.idioma_actual]["caracteres_idiomas"]).pack(pady=10)
        self.frame_caracteres = ttk.Frame(scrollable_frame)
        self.frame_caracteres.pack(pady=10, expand=True, fill='both')
    
        # Opciones de tamaño de plantilla
        medidas_plantilla = [
            self.traducciones[self.idioma_actual]["(2, 56)"],
            self.traducciones[self.idioma_actual]["(4, 28)"],
            self.traducciones[self.idioma_actual]["(7, 16)"],
            self.traducciones[self.idioma_actual]["(8, 14)"],
            self.traducciones[self.idioma_actual]["(14, 8)"],
            self.traducciones[self.idioma_actual]["(16, 7)"],
            self.traducciones[self.idioma_actual]["(28, 4)"],
            self.traducciones[self.idioma_actual]["(3, 56)"],
            self.traducciones[self.idioma_actual]["(4, 56)"],
            self.traducciones[self.idioma_actual]["(5, 56)"],
            self.traducciones[self.idioma_actual]["(7, 56)"],
            self.traducciones[self.idioma_actual]["(8, 56)"],
            self.traducciones[self.idioma_actual]["(10, 56)"],
            self.traducciones[self.idioma_actual]["(11, 56)"],
            self.traducciones[self.idioma_actual]["(14, 56)"],
            ]
        
        ttk.Label(scrollable_frame, text=self.traducciones[self.idioma_actual]["seleccionar_tamaño"]).pack(pady=10)
        self.medida_plantilla = ttk.Combobox(scrollable_frame, values=medidas_plantilla, font=("TkDefaultFont", self.medida_fuente))
        self.medida_plantilla.set(medidas_plantilla[0])
        self.medida_plantilla.pack(pady=10)
        self.medida_plantilla.bind("<<ComboboxSelected>>", self.actualizar_plantilla_texto)
    
        # Área para construir la plantilla
        ttk.Label(scrollable_frame, text=self.traducciones[self.idioma_actual]["plantilla_en_construccion"]).pack(pady=10)
        self.plantilla_texto = tk.Text(scrollable_frame, height=10, width=50, font=("TkDefaultFont", self.medida_fuente))
        self.plantilla_texto.pack(pady=10, expand=True, fill='both')
        self.plantilla_texto.bind('<Key>', self.manejar_insercion_manual)

        self.plantilla_texto.bind('<Control-a>', self.select_all)
        self.plantilla_texto.bind('<Control-c>', self.copy_text)
        self.plantilla_texto.bind('<Control-x>', self.cut_text)
        self.plantilla_texto.bind('<Control-v>', self.paste_text)
        
        # Evento para actualizar el contador al pegar texto
        self.plantilla_texto.bind('<<Paste>>', self.actualizar_plantilla_texto)
        self.plantilla_texto.bind('<<Modified>>', self.actualizar_plantilla_texto)
                
        # Frame para el contador de caracteres restantes y el botón de borrar último carácter
        frame_contador_botones = ttk.Frame(scrollable_frame)
        frame_contador_botones.pack(pady=10, fill='x')
        
        # Contador de caracteres restantes
        self.caracteres_restantes = tk.StringVar()
        self.caracteres_restantes.set(f"{self.traducciones[self.idioma_actual]['caracteres_restantes']}: {self.traducciones[self.idioma_actual]['112']}")
        ttk.Label(frame_contador_botones, textvariable=self.caracteres_restantes).grid(row=0, column=0, padx=5)

         # Botón de aleatoriedad
        ttk.Button(frame_contador_botones, text=self.traducciones[self.idioma_actual]["aleatoriedad"], command=self.aleatoriedad).grid(row=0, column=1, padx=5)
    
        # Botón para limpiar
        ttk.Button(frame_contador_botones, text=self.traducciones[self.idioma_actual]["limpiar"], command=self.limpiar_plantilla).grid(row=0, column=2, padx=5)
    
        # Botón para borrar el último carácter
        ttk.Button(frame_contador_botones, text=self.traducciones[self.idioma_actual]["borrar_caracter"], command=self.borrar_ultimo_caracter).grid(row=0, column=3, padx=5)
    
        # Asegúrate de que los botones estén centrados
        frame_contador_botones.grid_columnconfigure(0, weight=1)
        frame_contador_botones.grid_columnconfigure(4, weight=1)
    
        # Botones de guardar y salir
        frame_botones = ttk.Frame(scrollable_frame)
        frame_botones.pack(pady=10, fill='x')
        
        ttk.Button(frame_botones, text=self.traducciones[self.idioma_actual]["guardar_plantilla"], command=self.guardar_plantilla).pack(side="left", padx=5, expand=True)
        ttk.Button(frame_botones, text=self.traducciones[self.idioma_actual]["salir"], command=ventana_crear.destroy).pack(side="left", padx=5, expand=True)
        
        # Configuración final del canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Inicializar los caracteres
        self.actualizar_caracteres()
        
        return ventana_crear, scrollable_frame

    def aleatoriedad(self):
        contenido = self.plantilla_texto.get("1.0", tk.END).strip()
        filas = contenido.split('\n')
        nueva_plantilla = []
    
        for fila in filas:
            caracteres = [c.strip() for c in fila.split(',') if c.strip()]
            random.shuffle(caracteres)
            nueva_plantilla.append(caracteres)
    
        nuevo_contenido = '\n'.join([', '.join(fila) for fila in nueva_plantilla])
        self.plantilla_texto.delete("1.0", tk.END)
        self.plantilla_texto.insert(tk.END, nuevo_contenido)
        self.actualizar_plantilla_texto()
    
    def limpiar_plantilla(self):
        self.texto.delete(1.0, tk.END)
        for i in range(4):
            getattr(self, f"valor{i+1}").delete(0, tk.END)
        self.resultado.delete(1.0, tk.END)
        self.plantilla_texto.delete(1.0, tk.END)
        self.plantilla_texto.update()  # Forzar actualización del widget
        self.caracteres_usados.clear()
        self.actualizar_caracteres()
        self.actualizar_contador_caracteres()
        self.plantilla_actual = []  # Resetear la plantilla actual

    def manejar_insercion_manual(self, event):
        if event.char and event.char != '\x08':  # Ignora la tecla de retroceso
            if event.char != ',':  # Ignora las comas insertadas manualmente
                contenido_actual = self.plantilla_texto.get("1.0", tk.END).strip()
                caracteres_actuales = [c.strip() for c in contenido_actual.split(',') if c.strip()]
                
                if event.char not in caracteres_actuales:
                    if contenido_actual:
                        nuevo_contenido = contenido_actual + ', ' + event.char
                    else:
                        nuevo_contenido = event.char
                    
                    self.plantilla_texto.delete("1.0", tk.END)
                    self.plantilla_texto.insert(tk.END, nuevo_contenido)
                else:
                    messagebox.showwarning(self.traducciones[self.idioma_actual]["advertencia"], 
                                           self.traducciones[self.idioma_actual]["advertencia1"].format(event.char))
                    
                self.actualizar_plantilla_texto()
            return 'break'  # Evita la inserción predeterminada
        return None  # Permite otros eventos de teclado (como borrar)

    def bind_scroll_events(self, canvas):
        # Con Windows y MacOS
        canvas.bind("<MouseWheel>", lambda event: self.on_mouse_wheel(event, canvas))
        # Con Linux
        canvas.bind("<Button-4>", lambda event: self.on_mouse_wheel(event, canvas))
        canvas.bind("<Button-5>", lambda event: self.on_mouse_wheel(event, canvas))
    
    def on_mouse_wheel(self, event, canvas):
        if event.num == 5 or event.delta == -120:
            canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            canvas.yview_scroll(-1, "units")
            
    # Función para ajustar el tamaño de la ventana y widgets
    def ajustar_ventana(event):
        nuevo_ancho = self.ventana_crear.winfo_width()
        nuevo_alto = self.ventana_crear.winfo_height()
        nuevo_medida_fuente = min(nuevo_ancho, nuevo_alto) // 100
            
        self.estilo.configure("TCheckbutton", font=("TkDefaultFont", nuevo_medida_fuente))
        self.estilo.configure("TLabel", font=("TkDefaultFont", nuevo_medida_fuente))
        self.estilo.configure("TButton", font=("TkDefaultFont", nuevo_medida_fuente))
        self.medida_plantilla.configure(font=("TkDefaultFont", nuevo_medida_fuente))
        self.plantilla_texto.configure(font=("TkDefaultFont", nuevo_medida_fuente))
            
        # Ajustar el tamaño de los botones de caracteres
        for btn in self.botones_caracteres.values():
            btn.configure(font=("TkDefaultFont", nuevo_medida_fuente))
    
    def actualizar_caracteres(self):
        for widget in self.frame_caracteres.winfo_children():
            widget.destroy()
    
        row = 0
        for idioma, chars in self.caracteres_por_idioma.items():
            if self.idiomas_var[idioma][0].get(): 
                label_text = self.traducciones[self.idioma_actual].get(idioma, idioma)
                ttk.Label(self.frame_caracteres, text=label_text).grid(row=row, column=0, sticky="w")
                
                if idioma == "Numeros/signos": 
                    subcategorias = list(chars.keys())
                    subcategorias_traducidas = [self.traducciones[self.idioma_actual].get(sub, sub) for sub in subcategorias]
                    
                    if self.subcategoria_actual is None:
                        self.subcategoria_actual = subcategorias[0]
                    
                    self.subcategoria_var = tk.StringVar()
                    self.subcategoria_var.set(self.traducciones[self.idioma_actual].get(self.subcategoria_actual, self.subcategoria_actual))
                    
                    subcategoria_menu = ttk.Combobox(self.frame_caracteres, 
                                                     textvariable=self.subcategoria_var, 
                                                     values=subcategorias_traducidas,
                                                     font=("TkDefaultFont", self.medida_fuente),
                                                     state="readonly")
                    subcategoria_menu.grid(row=row, column=1, padx=5)
                    subcategoria_menu.bind("<<ComboboxSelected>>", self.actualizar_caracteres_subcategoria)
                    
                    subcategoria_menu.option_add('*TCombobox*Listbox.font', ("TkDefaultFont", self.medida_fuente))
                    
                    btn_agregar_todo = ttk.Button(self.frame_caracteres, 
                                                  text=self.traducciones[self.idioma_actual]["agregar_todos"], 
                                                  command=lambda: self.agregar_todos_caracteres(idioma, self.subcategoria_actual))
                    btn_agregar_todo.grid(row=row, column=2, padx=5)
                    
                    row += 1
                    
                    self.mostrar_caracteres_subcategoria(chars[self.subcategoria_actual], row)
                else:
                    btn_agregar_todo = ttk.Button(self.frame_caracteres, 
                                                  text=self.traducciones[self.idioma_actual]["agregar_todos"], 
                                                  command=lambda i=idioma: self.agregar_todos_caracteres(i))
                    btn_agregar_todo.grid(row=row, column=1, padx=5)
                    
                    row += 1
                    
                    self.mostrar_caracteres(chars, row)
                
                row += 2

    def get_subcategoria_original(self, subcategoria_traducida):
        for sub, sub_traducida in self.traducciones[self.idioma_actual].items():
            if sub_traducida == subcategoria_traducida:
                return sub
        return subcategoria_traducida  # Si no se encuentra una traducción, devuelve la entrada original
    
    def mostrar_caracteres(self, chars, row):
        col = 5
        for char in sorted(chars):
            btn = ttk.Button(self.frame_caracteres, text=char, width=2)
            btn.configure(command=lambda c=char, b=btn: self.insertar_caracter_wrapper(c, b))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.botones_caracteres[char] = btn
            col += 1
            if col > 21:  
                col = 5
                row += 1
    
    def mostrar_caracteres_subcategoria(self, chars, row):
        col = 5
        for char in sorted(chars):
            btn = ttk.Button(self.frame_caracteres, text=char, width=2) 
            btn.configure(command=lambda c=char, b=btn: self.insertar_caracter_wrapper(c, b))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.botones_caracteres[char] = btn
            col += 1
            if col > 21: 
                col = 5
                row += 1
 
    def insertar_caracter_wrapper(self, caracter, boton):
        try:
            if boton.winfo_exists():
                caracteres_restantes = self.actualizar_contador_caracteres()
                if caracteres_restantes > 0:
                    if caracter not in self.caracteres_usados:
                        self.insertar_caracter(caracter)
                        boton.state(['disabled'])
                    else:
                        messagebox.showwarning(self.traducciones[self.idioma_actual]["advertencia"], 
                                               self.traducciones[self.idioma_actual]["advertencia1"].format(caracter))
                else:
                    messagebox.showwarning(self.traducciones[self.idioma_actual]["advertencia"], 
                                           self.traducciones[self.idioma_actual]["advertencia2"])
            else:
                print(f"El botón para el carácter '{caracter}' ya no existe. Recreando el botón.")
                self.recrear_boton(caracter)
        except tk.TclError:
            self.recrear_boton(caracter)

    def recrear_boton(self, caracter):
        if caracter in self.botones_caracteres:
            del self.botones_caracteres[caracter]
        self.actualizar_caracteres()

    def cerrar_ventana_secundaria(self):
        # Otras operaciones de limpieza...
        for char in list(self.botones_caracteres.keys()):
            if not self.botones_caracteres[char].winfo_exists():
                del self.botones_caracteres[char]
        # Cerrar la ventana
        self.ventana_secundaria.destroy()
    
    def actualizar_caracteres_subcategoria(self, event):
        # Limpiar los caracteres existentes
        for widget in self.frame_caracteres.winfo_children():
            if isinstance(widget, ttk.Button) and widget.grid_info()['row'] > 0:
                widget.destroy()
        
        # Mostrar los caracteres de la nueva subcategoría seleccionada
        subcategoria_traducida = self.subcategoria_var.get()
        self.subcategoria_actual = self.get_subcategoria_original(subcategoria_traducida)
        
        # Limpiar solo los botones de caracteres, manteniendo otros widgets
        for widget in self.frame_caracteres.winfo_children():
            if isinstance(widget, ttk.Button) and widget.grid_info()['row'] > 0:
                widget.destroy()
        
        # Mostrar los caracteres de la nueva subcategoría seleccionada
        chars = self.caracteres_por_idioma["Numeros/signos"][self.subcategoria_actual]
        self.mostrar_caracteres_subcategoria(chars, 1)
        
        # Actualizar la interfaz
        self.actualizar_contador_caracteres()
        self.actualizar_plantilla_texto()
    
    def agregar_todos_caracteres(self, idioma, subcategoria=None):
        if idioma not in self.caracteres_por_idioma:
            messagebox.showerror(self.traducciones[self.idioma_actual]["error"], f"{idioma} no es un idioma válido")
            return
    
        if idioma == "Numeros/signos" and subcategoria:
            chars = self.caracteres_por_idioma[idioma][subcategoria]
        else:
            chars = self.caracteres_por_idioma[idioma]
    
        contenido_actual = self.plantilla_texto.get("1.0", tk.END).strip()
        caracteres_actuales = [c.strip() for c in contenido_actual.split(',') if c.strip()]
    
        nuevos_caracteres = []
        repetidos = []
        for char in chars:
            if char not in caracteres_actuales and char not in nuevos_caracteres:
                nuevos_caracteres.append(char)
            elif char not in repetidos:
                repetidos.append(char)
    
        if repetidos:
            mensaje = self.traducciones[self.idioma_actual]["advertencia1"].format(', '.join(repetidos))
            messagebox.showwarning(self.traducciones[self.idioma_actual]["advertencia"], mensaje)
    
        if nuevos_caracteres:
            todos_los_caracteres = caracteres_actuales + nuevos_caracteres
            
            medida_traducida = self.medida_plantilla.get()
            medida = self.obtener_medida_numerica(medida_traducida)
            caracteres_totales = medida[0] * medida[1]
            
            if len(todos_los_caracteres) > caracteres_totales:
                messagebox.showwarning(self.traducciones[self.idioma_actual]["advertencia"], 
                                       self.traducciones[self.idioma_actual]["advertencia2"])
                
                todos_los_caracteres = todos_los_caracteres[:caracteres_totales]
    
            nuevo_contenido = ', '.join(todos_los_caracteres)
            self.plantilla_texto.delete("1.0", tk.END)
            self.plantilla_texto.insert(tk.END, nuevo_contenido)
    
        # Actualizar la interfaz
        self.actualizar_caracteres()
        self.actualizar_contador_caracteres()
        self.actualizar_plantilla_texto()
            
    def insertar_caracter(self, caracter):
        if caracter in self.caracteres_usados:
            mensaje_advertencia = self.traducciones[self.idioma_actual]["advertencia1"].format(caracter)
            messagebox.showwarning(self.traducciones[self.idioma_actual]["advertencia"], mensaje_advertencia)
            return
    
        medida = self.obtener_medida_numerica(self.medida_plantilla.get())
        caracteres_totales = medida[0] * medida[1]
    
        contenido_actual = self.plantilla_texto.get("1.0", tk.END).strip()
        plantilla_actual = [row.split(', ') for row in contenido_actual.split('\n')] if contenido_actual else []
    
        # Añadir el nuevo carácter
        if not plantilla_actual or len(plantilla_actual[-1]) == medida[1]:
            if len(plantilla_actual) < medida[0]:
                plantilla_actual.append([caracter])
            else:
                plantilla_actual[-1].append(caracter)
        else:
            plantilla_actual[-1].append(caracter)
    
        # Verificar si se excedió el límite después de añadir
        caracteres_actuales = sum(len(row) for row in plantilla_actual)
        if caracteres_actuales > caracteres_totales:
            messagebox.showwarning(self.traducciones[self.idioma_actual]["advertencia"], self.traducciones[self.idioma_actual]["advertencia2"])
            
            # Eliminar caracteres sobrantes
            while caracteres_actuales > caracteres_totales:
                if plantilla_actual[-1]:
                    caracter_eliminado = plantilla_actual[-1].pop()
                    self.caracteres_usados.remove(caracter_eliminado)
                    caracteres_actuales -= 1
                if not plantilla_actual[-1] and len(plantilla_actual) > 1:
                    plantilla_actual.pop()
    
        self.plantilla_texto.delete("1.0", tk.END)
        plantilla_str = '\n'.join([', '.join([c if c != ' ' else '␣' for c in row]) for row in plantilla_actual])
        self.plantilla_texto.insert(tk.END, plantilla_str)
    
        self.caracteres_usados.add(caracter)
    
        # Actualizar contador de caracteres restantes
        caracteres_restantes = caracteres_totales - sum(len(row) for row in plantilla_actual)
        self.caracteres_restantes.set(f"{self.traducciones[self.idioma_actual]['caracteres_restantes']}: {caracteres_restantes}")
    
        # Actualizar la visualización de los caracteres disponibles
        self.actualizar_caracteres()
        
        # Llamar a actualizar_plantilla_texto para asegurar la consistencia
        self.actualizar_plantilla_texto()
        
    def actualizar_contador_caracteres(self):
        medida = self.obtener_medida_numerica(self.medida_plantilla.get())
        caracteres_totales = medida[0] * medida[1]
        contenido_actual = self.plantilla_texto.get("1.0", "end-1c").strip()
        caracteres_introducidos = len([char for char in contenido_actual.split(',') if char.strip()])
        caracteres_restantes = max(0, caracteres_totales - caracteres_introducidos)
        self.caracteres_restantes.set(f"{self.traducciones[self.idioma_actual]['caracteres_restantes']}: {caracteres_restantes}")
        return caracteres_restantes

    def actualizar_plantilla_texto(self, event=None):
        contenido_actual = self.plantilla_texto.get("1.0", tk.END).strip()
        if contenido_actual:
            caracteres = [char.strip() if char.strip() != '␣' else ' ' for char in contenido_actual.split(',')]
            medida_traducida = self.medida_plantilla.get()
            medida = self.obtener_medida_numerica(medida_traducida)
            filas = [caracteres[i:i+medida[1]] for i in range(0, len(caracteres), medida[1])]
            self.plantilla_actual = filas
            
            # Actualizar caracteres usados
            self.caracteres_usados = set(caracteres)
            
            # Actualizar contador de caracteres restantes
            caracteres_totales = medida[0] * medida[1]
            caracteres_restantes = max(0, caracteres_totales - len(caracteres))
            self.caracteres_restantes.set(f"{self.traducciones[self.idioma_actual]['caracteres_restantes']}: {caracteres_restantes}")
            
            # Actualizar la visualización de los caracteres disponibles
            self.actualizar_caracteres()
            
        self.plantilla_texto.edit_modified(False)

    def guardar_plantilla(self):
        def guardar():
            nombre_plantilla = entrada_nombre.get().strip()
            
            if nombre_plantilla:
                try:
                    contenido = self.plantilla_texto.get("1.0", tk.END).strip()
                    caracteres = [char.strip() for char in contenido.split(',') if char.strip()]
                    medida_seleccionado = self.obtener_medida_numerica(self.medida_plantilla.get())
                    nueva_plantilla = [caracteres[i:i+medida_seleccionado[1]] for i in range(0, len(caracteres), medida_seleccionado[1])]
                    
                    if len(nueva_plantilla) == medida_seleccionado[0] and all(len(row) == medida_seleccionado[1] for row in nueva_plantilla):
                        ruta_archivo = os.path.join(self.directorio_plantillas, f"{nombre_plantilla}.json")
                        with open(ruta_archivo, 'w', encoding='utf-8') as f:
                            json.dump(nueva_plantilla, f, ensure_ascii=False, indent=2)
                        
                        self.plantillas_personalizadas[nombre_plantilla] = nueva_plantilla
                        self.actualizar_lista_plantillas()
                        
                        messagebox.showinfo(self.traducciones[self.idioma_actual]["Nueva_plantilla_creada"], 
                                            self.traducciones[self.idioma_actual]['guardada_correctamente'].format(nombre_plantilla))
                        ventana_guardar.destroy()
                    else:
                        caracteres_faltantes = medida_seleccionado[0] * medida_seleccionado[1] - len(caracteres)
                        messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                             f"{self.traducciones[self.idioma_actual]['plantilla_no_coincide']} {caracteres_faltantes} {self.traducciones[self.idioma_actual]['caracteres']}.")
                except Exception as e:
                    print(f"Error al guardar plantilla: {e}")
                    messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                         self.traducciones[self.idioma_actual]["formato_invalido"])
            else:
                messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                     self.traducciones[self.idioma_actual]["nombre_plantilla_vacio"])
    
        ventana_guardar = tk.Toplevel(self)
        ventana_guardar.title(self.traducciones[self.idioma_actual]["guardar_plantilla"])
        ventana_guardar.geometry("400x150")
    
        label = tk.Label(ventana_guardar, 
                         text=self.traducciones[self.idioma_actual]["ingrese_nombre_plantilla"], 
                         font=("TkDefaultFont", self.medida_fuente))
        label.pack(pady=10)
    
        entrada_nombre = tk.Entry(ventana_guardar, font=("TkDefaultFont", self.medida_fuente))
        entrada_nombre.pack(pady=10, padx=20, fill=tk.X)
    
        frame_botones = tk.Frame(ventana_guardar)
        frame_botones.pack(pady=10)
    
        boton_guardar = tk.Button(frame_botones, 
                                  text=self.traducciones[self.idioma_actual]["guardar_plantilla"],
                                  command=guardar, 
                                  font=("TkDefaultFont", self.medida_fuente))
        boton_guardar.pack(side=tk.LEFT, padx=5)
    
        boton_cancelar = tk.Button(frame_botones, 
                                   text=self.traducciones[self.idioma_actual]["cancelar"], 
                                   command=ventana_guardar.destroy, 
                                   font=("TkDefaultFont", self.medida_fuente))
        boton_cancelar.pack(side=tk.LEFT, padx=5)
    
        # Centrar la ventana
        ventana_guardar.update_idletasks()
        width = ventana_guardar.winfo_width()
        height = ventana_guardar.winfo_height()
        x = (ventana_guardar.winfo_screenwidth() // 2) - (width // 2)
        y = (ventana_guardar.winfo_screenheight() // 2) - (height // 2)
        ventana_guardar.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
        ventana_guardar.focus_set()
        entrada_nombre.focus()
  
        # Función para actualizar el tamaño de la fuente
        def actualizar_fuente(event=None):
            nuevo_tamano = self.medida_fuente
            label.config(font=("TkDefaultFont", nuevo_tamano))
            entrada_nombre.config(font=("TkDefaultFont", nuevo_tamano))
            boton_guardar.config(font=("TkDefaultFont", nuevo_tamano))
            boton_cancelar.config(font=("TkDefaultFont", nuevo_tamano))
    
        # Vincular la función de actualización al evento de configuración
        ventana_guardar.bind("<Configure>", actualizar_fuente)
    
        # Llamar a la función una vez para aplicar el tamaño inicial
        actualizar_fuente()
                
    def editar_plantilla(self):
        self.ventana_editar = tk.Toplevel(self)
        self.ventana_editar.title(self.traducciones[self.idioma_actual]["editar_plantilla_existente"])
        self.ventana_editar.geometry("500x200")
    
        # Cargar plantillas desde la carpeta
        self.cargar_plantillas_desde_archivos()
    
        # Lista de plantillas personalizadas
        plantillas_a_editar = list(self.plantillas_personalizadas.keys())
    
        if not plantillas_a_editar:
            messagebox.showinfo(self.traducciones[self.idioma_actual]["info"], self.traducciones[self.idioma_actual]["No_hay_plantillas_nuevas_creadas_para_editar"])
            self.ventana_editar.destroy()
            return
    
        tk.Label(self.ventana_editar, text=self.traducciones[self.idioma_actual]["Selecciona_la_plantilla_a_editar"], font=("TkDefaultFont", self.medida_fuente)).pack(pady=10)
        self.plantilla_seleccionada = tk.StringVar()
        self.plantilla_seleccionada.set(plantillas_a_editar[0])
        
        self.menu_plantillas = ttk.Combobox(self.ventana_editar, textvariable=self.plantilla_seleccionada, values=plantillas_a_editar, font=("TkDefaultFont", self.medida_fuente))
        self.menu_plantillas.pack(pady=10)
    
        # Frame para los botones
        frame_botones = tk.Frame(self.ventana_editar)
        frame_botones.pack(pady=10)
    
        # Botón Editar
        ttk.Button(frame_botones, text=self.traducciones[self.idioma_actual]["editar"], 
                   command=lambda: [self.abrir_editor_plantilla(), self.ventana_editar.destroy()], 
                   style='TButton').pack(side=tk.LEFT, padx=5)
    
        # Botón Eliminar
        ttk.Button(frame_botones, text=self.traducciones[self.idioma_actual]["eliminar"], command=self.eliminar_plantilla, style='TButton').pack(side=tk.LEFT, padx=5)
    
        # Botón Cancelar
        ttk.Button(frame_botones, text=self.traducciones[self.idioma_actual]["cancelar"], command=self.ventana_editar.destroy, style='TButton').pack(side=tk.LEFT, padx=5)
    
        # Aplicar estilos y configuraciones
        self.aplicar_estilos_ventana(self.ventana_editar)
    
        # Vincular la función de actualización al evento de redimensionamiento
        self.ventana_editar.bind("<Configure>", lambda event: self.actualizar_ventana_dinamica(self.ventana_editar))
    
    def cargar_plantillas_desde_archivos(self):
        self.plantillas_personalizadas.clear()
        for archivo in os.listdir(self.directorio_plantillas):
            if archivo.endswith('.json'):
                nombre_plantilla = os.path.splitext(archivo)[0]
                ruta_archivo = os.path.join(self.directorio_plantillas, archivo)
                try:
                    with open(ruta_archivo, 'r', encoding='utf-8') as f:
                        plantilla = json.load(f)
                    self.plantillas_personalizadas[nombre_plantilla] = plantilla
                except Exception as e:
                    print(f"Error al cargar la plantilla {nombre_plantilla}: {e}")
                    
    def aplicar_estilos_ventana(self, ventana):
        for widget in ventana.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(font=("TkDefaultFont", self.medida_fuente))
            elif isinstance(widget, ttk.Combobox):
                widget.configure(font=("TkDefaultFont", self.medida_fuente))
                widget.option_add('*TCombobox*Listbox.font', ("TkDefaultFont", self.medida_fuente))
            elif isinstance(widget, tk.Frame):
                self.aplicar_estilos_ventana(widget)  # Aplicar recursivamente a los widgets dentro del frame
    
    def eliminar_plantilla(self):
        plantilla_seleccionada = self.plantilla_seleccionada.get()
        if plantilla_seleccionada in self.plantillas_personalizadas:
            confirmacion = messagebox.askyesno(
                self.traducciones[self.idioma_actual]["confirmar"],
                self.traducciones[self.idioma_actual]["confirmar_eliminar_plantilla"].format(plantilla_seleccionada)
            )
            if confirmacion:
                del self.plantillas_personalizadas[plantilla_seleccionada]
                self.actualizar_menu_plantillas()
                messagebox.showinfo(self.traducciones[self.idioma_actual]["info"], self.traducciones[self.idioma_actual]["plantilla_eliminada"])
                # No cerramos la ventana aquí, permitiendo al usuario seguir editando o eliminando otras plantillas
        else:
            messagebox.showerror(self.traducciones[self.idioma_actual]["error"], self.traducciones[self.idioma_actual]["plantilla_no_encontrada"])

    def abrir_editor_plantilla(self):
        seleccionada = self.plantilla_seleccionada.get()
        ventana_crear, scrollable_frame = self.crear_plantilla()
        editar_plantilla_texto = self.traducciones[self.idioma_actual].get("editar_plantilla", "Editar Plantilla")
        ventana_crear.title(f"{editar_plantilla_texto}: {seleccionada}")
    
        plantilla = self.plantillas_personalizadas[seleccionada]
        self.plantilla_texto.delete("1.0", tk.END)
        plantilla_str = ', '.join([', '.join(row) for row in plantilla])
        self.plantilla_texto.insert(tk.END, plantilla_str)
    
        # Encontrar la medida de la plantilla
        filas = len(plantilla)
        columnas = len(plantilla[0]) if plantilla else 0
        medida = f"({filas}, {columnas})"
        self.medida_plantilla.set(medida)
    
        caracteres_faltantes = filas * columnas - sum(len(row) for row in plantilla)
        # Corregido: usar el diccionario correctamente
        self.caracteres_restantes.set(f"{self.traducciones[self.idioma_actual]['caracteres_restantes']}: {caracteres_faltantes}")
    
        self.caracteres_usados = set(char for row in plantilla for char in row)
        self.actualizar_caracteres()
    
        # Asegurarse de que la ventana se actualice correctamente
        self.actualizar_ventana_dinamica(ventana_crear)

    def borrar_ultimo_caracter(self):
        contenido_actual = self.plantilla_texto.get("1.0", tk.END).strip()
        if contenido_actual:
            caracteres = [char.strip() for char in contenido_actual.split(',') if char.strip()]
            if caracteres:
                caracter_borrado = caracteres.pop()
                if caracter_borrado in self.caracteres_usados:
                    self.caracteres_usados.remove(caracter_borrado)
                
                # Reconstruir la plantilla
                medida = self.obtener_medida_numerica(self.medida_plantilla.get())
                plantilla_actual = [caracteres[i:i+medida[1]] for i in range(0, len(caracteres), medida[1])]
                
                # Actualizar el texto en la caja
                self.plantilla_texto.delete("1.0", tk.END)
                plantilla_str = ', '.join([', '.join(row) for row in plantilla_actual])
                self.plantilla_texto.insert(tk.END, plantilla_str)
                
                # Actualizar caracteres y contador
                self.actualizar_caracteres()
                self.actualizar_contador_caracteres()
                
                # Habilitar el botón del carácter borrado
                for idioma, chars in self.caracteres_por_idioma.items():
                    if caracter_borrado in chars:
                        if caracter_borrado in self.botones_caracteres:
                            self.botones_caracteres[caracter_borrado].state(['!disabled'])

    def limpiar(self):
        self.texto.delete(1.0, tk.END)
        for i in range(4):
            getattr(self, f"valor{i+1}").delete(0, tk.END)
        self.resultado.delete(1.0, tk.END)
        self.plantilla_texto.delete(1.0, tk.END)
        self.plantilla_texto.update()  # Forzar actualización del widget
        self.caracteres_usados.clear()
        self.plantilla_actual = []  # Resetear la plantilla actual
        self.actualizar_caracteres(reset=True)  # Añadimos un parámetro para indicar un reset completo
        self.actualizar_contador_caracteres()

    def ejecutar(self):
        texto = self.texto.get("1.0", tk.END)
        caja1 = self.valor1.get()
        caja2 = self.valor2.get()
        caja3 = self.valor3.get()
        caja4 = self.valor4.get()
    
        if not all([caja1, caja2, caja3, caja4]):
            messagebox.showwarning(self.traducciones[self.idioma_actual]["error"],
                                   self.traducciones[self.idioma_actual]["error_ingresar_valores"])
            return
    
        if not all(c.isdigit() and 0 <= int(c) <= 1000 for c in [caja1, caja2, caja3, caja4]):
            messagebox.showerror(self.traducciones[self.idioma_actual]["error"],
                         self.traducciones[self.idioma_actual]["error_valores_numeros"])
            return
    
        plantilla_seleccionada = self.plantilla.get()
        teclado = self.obtener_layout_plantilla(plantilla_seleccionada)

        if teclado is None:
            messagebox.showerror(self.traducciones[self.idioma_actual]["error"],
                         self.traducciones[self.idioma_actual]["No_plantilla_seleccionada_no_existe"])
            return
    
        if self.opcion.get() == "cifrar":
            resultado = self.cifrar(texto, caja1, caja2, caja3, caja4, teclado)
        elif self.opcion.get() == "descifrar":
            resultado = self.descifrar(texto, caja1, caja2, caja3, caja4, teclado)
        else:
            messagebox.showinfo(self.traducciones[self.idioma_actual]["info2"],
                                self.traducciones[self.idioma_actual]["info_funcion_no_implementada"])
            return
    
        self.resultado.delete(1.0, tk.END)
        self.resultado.insert(tk.END, resultado)

    pass

    # Función para solicitar contraseña
    def solicitar_contraseña(self, texto):
        intentos = 0
        while intentos < 3:
            contraseña = simpledialog.askstring(self.traducciones[self.idioma_actual]["contraseña_requerida"],
                                                self.traducciones[self.idioma_actual]["ingresa_contraseña"])
            if contraseña is None:
                return False
            if texto == contraseña:
                return True
            else:
                intentos += 1
                if intentos < 3: 
                    messagebox.showerror(self.traducciones[self.idioma_actual]["error"],
                                     self.traducciones[self.idioma_actual]["intenta_nuevamente"])
        
        if intentos == 3:
            messagebox.showwarning(self.traducciones[self.idioma_actual]["error"],
                             self.traducciones[self.idioma_actual]["excedido_intentos_mensaje"])
            return False
    
        return False

    def cifrar(self, texto, caja1, caja2, caja3, caja4, teclado):
        resultado = self.ocultar_palabra(texto, caja1, caja2, caja3, caja4, teclado, "cifrar")
    
        contraseña = None
        for i in range(len(texto)):
            if texto[i] in "¢|@#~½¶←↓→ˀ|¢ª─¬" and i + 8 < len(texto):
                contraseña = texto[i:i+8]
                break
    
        if contraseña:
            if self.solicitar_contraseña(contraseña):
                return resultado  # Devolver el texto cifrado si la contraseña es correcta
            else:
                return ""  # No mostrar resultado si la contraseña es incorrecta o cancelada
        else:
            return resultado  # Devolver el texto cifrado si no hay contraseña especial

    def descifrar(self, texto, caja1, caja2, caja3, caja4, teclado):
        resultado = self.ocultar_palabra(texto, -int(caja1), -int(caja2), -int(caja3), -int(caja4), teclado, "descifrar")
        
        # Verificar si hay caracteres especiales en el texto
        simbolos_reconocidos = "¢|@#~½¶←↓→ˀ|¢ª─¬"
        segmento_para_descifrar = None
        
        # Buscar el símbolo especial y obtener el segmento para descifrar
        for i in range(len(texto)):
            if texto[i] in simbolos_reconocidos and i + 8 < len(texto):
                segmento_para_descifrar = texto[i:i+8]
                break  # Salir del bucle al encontrar el símbolo
        
        if segmento_para_descifrar:
            parte_descifrada = self.ocultar_palabra(segmento_para_descifrar, -int(caja1), -int(caja2), -int(caja3), -int(caja4), teclado, "descifrar")
            if not self.solicitar_contraseña(parte_descifrada):
                return ""  # Salir de la función si la contraseña es incorrecta
        
        return resultado
        
    # Función para cifrar y descifrar palabras
    def ocultar_palabra(self, palabra, caja1, caja2, caja3, caja4, teclado, modo):
        simbolos_reconocidos = "¢|@#~½¶←↓→ˀ|¢ª─¬"
        resultado = ''
        
        def encontrar_posicion(caracter):
            caracter_lower = caracter.lower()
            for i, fila in enumerate(teclado):
                if caracter_lower in [c.lower() for c in fila]:
                    return i, [c.lower() for c in fila].index(caracter_lower)
            return None, None
    
        espacio_en_plantilla = '␣' in [char for row in teclado for char in row]
        indice = len(palabra)
        
        for i, caracter in enumerate(palabra):
            if caracter in simbolos_reconocidos:
                resultado += caracter
                continue
    
            caracter_busqueda = caracter.lower() if caracter != ' ' else '␣'
            fila, columna = encontrar_posicion(caracter_busqueda)
            
            if fila is not None and columna is not None:
                columna += int(caja1) - indice
                fila += int(caja2) - indice
                columna -= int(caja3) - indice
                fila -= int(caja4) - indice
                
                fila %= len(teclado)
                columna %= len(teclado[fila])
                
                nuevo_caracter = teclado[fila][columna]
                if modo == "descifrar" and nuevo_caracter == '␣':
                    nuevo_caracter = ' '
                if caracter.isupper():
                    nuevo_caracter = nuevo_caracter.upper()
                resultado += nuevo_caracter
            else:
                if caracter == ' ' and not espacio_en_plantilla:
                    resultado += ' '  # Mantener el espacio si no está en la plantilla
                else:
                    resultado += caracter  # Mantener el carácter original si no está en la plantilla
    
        return resultado

    def actualizar_todas_ventanas(self):
        # Actualiza la ventana principal
        self.actualizar_widgets_recursivamente(self)
        
        # Actualiza todas las ventanas secundarias
        for ventana in self.winfo_children():
            if isinstance(ventana, tk.Toplevel):
                self.actualizar_widgets_recursivamente(ventana)
        
        if hasattr(self, 'ventana_caracteres'):
            self.actualizar_widgets_recursivamente(self.ventana_caracteres)
    
    def actualizar_ventana_dinamica(self, ventana):
        self.actualizar_widgets_recursivamente(ventana)
        # Actualizar cualquier otro elemento específico de la ventana si es necesario
    
    def actualizar_widgets_recursivamente(self, widget):
        style = ttk.Style()
        style.configure('.', font=("TkDefaultFont", self.medida_fuente))
    
        for child in widget.winfo_children():
            if isinstance(child, (tk.Label, tk.Button, tk.Radiobutton, tk.Checkbutton, tk.Entry, tk.Text)):
                child.configure(font=("TkDefaultFont", self.medida_fuente))
            elif isinstance(child, ttk.Combobox):
                child.configure(font=("TkDefaultFont", self.medida_fuente))
                child.option_add('*TCombobox*Listbox.font', ("TkDefaultFont", self.medida_fuente))
            
            # Recursivamente actualiza los widgets hijos
            self.actualizar_widgets_recursivamente(child)
    
    def obtener_traduccion(self, clave):
        for key, value in self.traducciones[self.idioma_actual].items():
            if value == clave or key == clave:
                return self.traducciones[self.idioma_actual][key]
        return clave  # Si no se encuentra una traducción, devuelve la clave original
    
    def actualizar_textos(self):
        # Actualizar textos de la interfaz
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Radiobutton):
                widget.configure(text=self.traducciones[self.idioma_actual][widget.cget("text")])
            elif isinstance(widget, ttk.Button):
                widget.configure(text=self.traducciones[self.idioma_actual][widget.cget("text")])
            # Asegurarse de que el tamaño de fuente se mantiene
            if hasattr(widget, 'configure'):
                widget.configure(font=("TkDefaultFont", self.medida_fuente))
        
        self.boton_ajustes.configure(text="")
        self.boton_ajustes.image = None  # Limpiar la imagen anterior
        icono_pil = self.crear_icono()
        icono_tk = ImageTk.PhotoImage(icono_pil)
        self.boton_ajustes.configure(image=icono_tk)
        self.boton_ajustes.image = icono_tk
    
    # Asegúrate de que este método esté en tu clase
    def configurar_estilos(self):
        style = ttk.Style()
        font = ("TkDefaultFont", self.medida_fuente)
        style.configure('.', font=font)
        style.configure("TButton", font=font)
        style.configure("TLabel", font=font)
        style.configure("TRadiobutton", font=font)
        style.configure("TCheckbutton", font=font)
        style.configure("TEntry", font=font)
        style.configure("TCombobox", font=font)
        style.map("TCombobox", fieldbackground=[("readonly", "white")])
        style.configure("Combobox.Listbox", font=font)

    def cambiar_tamano_letra(self):
        def aplicar_tamano():
            try:
                nuevo_tamano = int(entrada_tamano.get())
                if 8 <= nuevo_tamano <= 24:  # Limitar el tamaño entre 8 y 24
                    self.medida_fuente = nuevo_tamano
                    self.actualizar_tamano_fuente()
                    ventana_tamano.destroy()  # Cierra la ventana después de aplicar cambios
                else:
                    messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                         self.traducciones[self.idioma_actual]["tamano_fuera_rango"])
            except ValueError:
                messagebox.showerror(self.traducciones[self.idioma_actual]["error"], 
                                     self.traducciones[self.idioma_actual]["numero_invalido"])
    
        def cancelar():
            ventana_tamano.destroy()  # Cierra la ventana sin aplicar cambios
    
        ventana_tamano = tk.Toplevel(self)
        ventana_tamano.title(self.traducciones[self.idioma_actual]["cambiar_tamano_letra"])
        ventana_tamano.geometry("350x150")
    
        ttk.Label(ventana_tamano, text=self.traducciones[self.idioma_actual]["nuevo_tamano_letra"], 
                  font=("TkDefaultFont", self.medida_fuente)).pack(pady=5)
    
        entrada_tamano = ttk.Entry(ventana_tamano, font=("TkDefaultFont", self.medida_fuente))
        entrada_tamano.insert(0, str(self.medida_fuente))
        entrada_tamano.pack(pady=5)
    
        ttk.Button(ventana_tamano, text=self.traducciones[self.idioma_actual]["aplicar"], 
                   command=aplicar_tamano, 
                   style='TButton').pack(pady=5, side=tk.LEFT, padx=10)
    
        ttk.Button(ventana_tamano, text=self.traducciones[self.idioma_actual]["cancelar"], 
                   command=cancelar, 
                   style='TButton').pack(pady=5, side=tk.RIGHT, padx=10)
    
        # Centrar la ventana
        ventana_tamano.update_idletasks()
        width = ventana_tamano.winfo_width()
        height = ventana_tamano.winfo_height()
        x = (ventana_tamano.winfo_screenwidth() // 2) - (width // 2)
        y = (ventana_tamano.winfo_screenheight() // 2) - (height // 2)
        ventana_tamano.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def actualizar_tamano_fuente(self):
        self.configurar_estilos()
        self.actualizar_todas_ventanas()
        # Si necesitas actualizar el menú, asegúrate de que crear_menu sea un método válido
        # self.config(menu=self.crear_menu())  
                
    def mostrar_consejos(self):
        if hasattr(self, 'ventana_consejos'):
            try:
                self.ventana_consejos.lift()
                self.ventana_consejos.update()
                return
            except tk.TclError:
                del self.ventana_consejos
        
        self.ventana_consejos = tk.Toplevel(self)
        self.ventana_consejos.title(self.traducciones[self.idioma_actual]["consejos"])
        self.ventana_consejos.geometry("600x400")
    
        frame = ttk.Frame(self.ventana_consejos)
        frame.pack(expand=True, fill='both')
    
        texto = tk.Text(frame, wrap='word', font=("TkDefaultFont", self.medida_fuente))
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=scrollbar.set)
    
        scrollbar.pack(side="right", fill="y")
        texto.pack(side="left", expand=True, fill="both")
    
        # Comprobar si consejos_texto está definido correctamente
        if not hasattr(self, 'consejos_texto'):
            self.definir_consejos_texto()
    
        consejos = self.consejos_texto.get(self.idioma_actual, self.consejos_texto["Español"])
        texto.insert("1.0", consejos)
        texto.config(state="disabled")
    
        self.ventana_consejos.protocol("WM_DELETE_WINDOW", self.cerrar_ventana_consejos)
    
    def cerrar_ventana_consejos(self):
        if hasattr(self, 'ventana_consejos'):
            self.ventana_consejos.destroy()
            del self.ventana_consejos

    def faq(self):
        if hasattr(self, 'ventana_faq'):
            try:
                self.ventana_faq.lift()
                self.ventana_faq.update()
                return
            except tk.TclError:
                del self.ventana_faq
        
        self.ventana_faq = tk.Toplevel(self)
        self.ventana_faq.title(self.traducciones[self.idioma_actual]["faq"])
        self.ventana_faq.geometry("600x400")
        
        frame = ttk.Frame(self.ventana_faq)
        frame.pack(expand=True, fill='both')
        
        texto = tk.Text(frame, wrap='word', font=("TkDefaultFont", self.medida_fuente))
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        texto.pack(side="left", expand=True, fill="both")
        
        # Comprobar si faq_texto está definido correctamente
        if not hasattr(self, 'faq_texto'):
            self.definir_faq_texto()
        
        faq_texto = self.faq_texto.get(self.idioma_actual, self.faq_texto["Español"])
        texto.insert("1.0", faq_texto)
        texto.config(state="disabled")
        self.ventana_faq.protocol("WM_DELETE_WINDOW", self.cerrar_ventana_faq)

    def cerrar_ventana_faq(self):
        if hasattr(self, 'ventana_faq'):
            self.ventana_faq.destroy()
            del self.ventana_faq
   
    def mostrar_creditos(self):
        if hasattr(self, 'ventana_creditos'):
            self.ventana_creditos.lift()
            return
    
        self.ventana_creditos = tk.Toplevel(self)
        self.ventana_creditos.title(self.traducciones[self.idioma_actual]["creditos"])
        self.ventana_creditos.geometry("600x400")
    
        frame = ttk.Frame(self.ventana_creditos)
        frame.pack(expand=True, fill='both')
    
        texto = tk.Text(frame, wrap='word', font=("TkDefaultFont", self.medida_fuente))
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        texto.pack(side="left", expand=True, fill="both")
    
        creditos_texto = self.creditos_texto.get(self.idioma_actual, self.creditos_texto["Español"])
        texto.insert("1.0", creditos_texto)
        texto.config(state="disabled")
    
        self.ventana_creditos.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana_creditos())
    
    def cerrar_ventana_creditos(self):
        self.ventana_creditos.destroy()
        del self.ventana_creditos 

    def licencia(self):
        if hasattr(self, 'ventana_licencia'):
            self.ventana_licencia.lift()
            return
    
        self.ventana_licencia = tk.Toplevel(self)
        self.ventana_licencia.title(self.traducciones[self.idioma_actual]["licencia"])
        self.ventana_licencia.geometry("600x400")
    
        frame = ttk.Frame(self.ventana_licencia)
        frame.pack(expand=True, fill='both')
    
        texto = tk.Text(frame, wrap='word', font=("TkDefaultFont", self.medida_fuente))
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        texto.pack(side="left", expand=True, fill="both")
    
        licencia_texto = self.licencia_texto.get(self.idioma_actual, self.licencia_texto["Español"])
        texto.insert("1.0", licencia_texto)
        texto.config(state="disabled")
    
        self.ventana_licencia.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana_licencia())

    def cerrar_ventana_licencia(self):
        self.ventana_licencia.destroy()
        del self.ventana_licencia

if __name__ == "__main__":
    app = LIVENCRYPT()
    app.mainloop()


