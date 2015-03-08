"""
A beta script which takes the output of OWASP Dependency-Check and outputs an excel document.
This script also includes exploit resolution from exploit-db.com

Input:  "dependency-check-report.xml"
Output:  "Dependency-Vulnerabilities.xlsx"
Usage:  python dp2xl.py <Input XML> <Output XLSX>

"""


__author__ = "Arthur Hinds (ahinds@cigital.com)"


from xml.dom import minidom
from bs4 import BeautifulSoup
import re
import urllib
import xlsxwriter
import copy
import sys

class cveClass:
    def __init__(self):
        pass
    component = ""
    name = ""
    dependency_name = ""
    score = 0.0
    severity = ""
    description = ""
    exploit = "Undetermined"
    def setName(self, name):
        self.name = name
        pass
    def setCompnent(self, component):
        self.component = component
        pass
    def setSeverity(self, severity):
        self.severity = severity
        pass
    def setDependencyName(self, dname):
        self.dependency_name = dname
        pass
    def setScore(self, score):
        self.score = score
        pass
    def setDescription(self, desc):
        self.description = desc
        pass
    def findExploit(self):
        try:
            exploitDoc = BeautifulSoup(urllib.urlopen("http://www.exploit-db.com/search/?action=search&filter_page=1&filter_description=&filter_exploit_text=&filter_author=&filter_platform=0&filter_type=0&filter_lang_id=0&filter_port=&filter_osvdb=&filter_cve=" + self.name[4:]))
            if len(exploitDoc.find_all(text=re.compile("No results"))) < 1:
                self.exploit = True
                pass
            pass
        except IOError:
            print "Error Getting " + self.name
            self.exploit = "Undetermined"
            pass
        pass

def howtouse():
    print "python dp2xl.py <input xml> <output excel>"
    print "TODO:  Exploit Threads, Formatting"


def main():

    #Let's parse args first
    if len(sys.argv) < 3:
        howtouse()
        quit()
        pass
    args = sys.argv

    #Check for file, filesystem write priv and connectivity
    try:
        xmldoc = minidom.parse(sys.argv[1])
        print ("Parsing XML Data..")
        dependencies = xmldoc.getElementsByTagName("dependency")
        pass
    except IOError:
        print "Failed to read file, quitting"
        quit()
        pass

    allcves = []
    for dependency in dependencies:
        vulnerabilities = dependency.getElementsByTagName("vulnerability")
        if len(vulnerabilities) > 0:
            for vulnerability in vulnerabilities:
                tempcve = cveClass()
                tempcve.setName(vulnerability.getElementsByTagName("name")[0].firstChild.data)
                tempcve.setScore(vulnerability.getElementsByTagName("cvssScore")[0].firstChild.data)
                tempcve.setDescription(vulnerability.getElementsByTagName("description")[0].firstChild.data)
                tempcve.setSeverity(vulnerability.getElementsByTagName("severity")[0].firstChild.data)
                tempcve.setCompnent(dependency.getElementsByTagName("fileName")[0].firstChild.data)
                allcves.append(copy.copy(tempcve))
                pass
            pass
        pass

    print "Searching for Exploits"
    for cve in allcves:
        cve.findExploit()
        pass

    print ("creating excel")
    workbook = xlsxwriter.Workbook(sys.argv[2])
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, "Component")
    worksheet.write(0, 1, "CVE")
    worksheet.write(0, 2, "CVSS Score")
    worksheet.write(0, 3, "Severity")
    worksheet.write(0, 4, "Public Exploit")
    worksheet.write(0, 5, "Description")
    row = 1

    for cve in allcves:
        worksheet.write(row, 0, cve.component)
        worksheet.write(row, 1, cve.name)
        worksheet.write(row, 2, cve.score)
        worksheet.write(row, 3, cve.severity)
        if cve.exploit == True:
            worksheet.write(row, 4, "Yes")
            pass
        elif cve.exploit == "Undetermined":
            worksheet.write(row, 4, "Undetermined")
            pass
        else:
            worksheet.write(row, 4, "No")
            pass
        worksheet.write(row, 5, str(cve.description))
        row += 1

    workbook.close()

if __name__ == '__main__':
    main()
