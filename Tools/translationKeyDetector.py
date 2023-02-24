#for detecting all .py files under ../UI folder, check if any translation key is missing or redundant. output to csv file.
import re, os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","Core"))
from Core import appManager

if __name__ == '__main__':
    translationKeys = appManager.translationData.keys()
    languages = appManager.config.languages
    print("languages: ",languages)
    keysNeedAdd = []
    keysNeedRemove = []
    allRawTextsInPython = []
    allKeysInPython = []
    directoryNeedCheck = [os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "UI"),
                          os.path.join(os.path.dirname(os.path.realpath(__file__)),"..", "Core"),
                          os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "ExternalPackage")]

    #find all possible keys first
    for directory in directoryNeedCheck:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py") and not file.startswith("translationKeyDetector") and not file.startswith("translator"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        wholeFile = f.read()

                        #auto translation word
                        matches = re.findall(re.compile('AutoTranslateWord[ ]*?\\(.?r?(?P<quote1>[\'\"])(?P<text1>.+?)(?P=quote1).*?\\)|translate[ ]*?\\(r?(?P<quote2>[\'\"])(?P<text2>.+?)(?P=quote2)',re.S),wholeFile)
                        if len(matches) > 0:
                            for match in matches:
                                if match[1] != '':
                                    allRawTextsInPython.append(match[1])
                                elif match[3] != '':
                                    allRawTextsInPython.append(match[3])

                        #auto translation key
                        listMatches = re.findall(re.compile(r'AutoTranslateWordList[ ]*?\([ ]*?(?P<text>.+?)[ ]*?\)',re.S),wholeFile)
                        for match in listMatches:
                            content = match
                            if content[0] == '(':
                                content = content[1:]
                            elif content[0] == '[':
                                content = content[1:-1]
                            for word in re.finditer(re.compile('(:?[\'\"])(?P<text>.*?)\\1',re.S), content):
                                allRawTextsInPython.append(word['text'])

                        #auto translation enum
                        match = re.search(r'class .+?\(AutoTranslateEnum\):.*?\n?((\n[ ]+.+?[ ]?=[ ]?[0-9]{1,}){1,})', wholeFile, re.S)
                        if match is not None and match.group(1) is not None:
                            for key in [s.replace(' ', '').split('=')[0] for s in match.group(1).split('\n')]:
                                if key != '':
                                    allRawTextsInPython.append(key)

                        print("checked file: ", directory.split('\\')[-1]+'\\'+file)

    #one single key, or split word combination
    for rawText in allRawTextsInPython:
        rawText_edited = str(rawText).lower()
        matches = re.findall(re.compile(r'(?<!\\)\[(.*?)(?<!\\)\]',re.S), rawText_edited)
        if len(matches) == 0:
            allKeysInPython.append(rawText_edited)
        else:
            for match in matches:
                if str(match) not in allKeysInPython:
                    allKeysInPython.append(str(match))

    print("\nallKeysInPython: ", allKeysInPython, "\n")

    for key in allKeysInPython:
        lkey = key.lower()
        if lkey not in translationKeys and lkey not in keysNeedAdd:
            keysNeedAdd.append(lkey)
    for key in translationKeys :
        lkey = key.lower()
        if lkey not in allKeysInPython and lkey not in keysNeedRemove and lkey not in languages:
            keysNeedRemove.append(lkey)

    print("Keys need add: {}\n".format(keysNeedAdd))
    print("Keys need remove: {}\n".format(keysNeedRemove))

    if len(keysNeedAdd) > 0 or len(keysNeedRemove) > 0:
        with open(appManager.TRANSLATION_DATA_PATH,'r', encoding='utf-8') as originFile:
            lines = originFile.readlines()
            for line in lines.copy():
                if ',' in line: #data line
                    splits = re.split(r'(?<!\\),', line)
                    if splits[0].lower().replace(r'\,',r',') in keysNeedRemove and splits[0].lower() not in keysNeedAdd+languages:
                        lines.remove(line)
            for key in keysNeedAdd:
                lines.append(key.replace(',',r'\,') + '{}\n'.format(','*len(languages)))

        if input("Do you want to save changes? (y/n) \n") == 'y':
            with open(appManager.TRANSLATION_DATA_PATH,'w+', encoding='utf-8') as originFile:
                originFile.writelines(lines)
            print("Changes saved")
        else:
            print("Changes not saved, quited.")
    else:
        print("No changes needed, quited.")