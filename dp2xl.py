"""
A beta script which takes the output of OWASP Dependency-Check and outputs an excel document.
This script also includes exploit resolution from exploit-db.com

Input:  "dependency-check-report.xml"
Output:  "Dependency-Vulnerabilities.xlsx"
Usage:  Run this script in the directory where the input file exists.

"""


__author__ = "Arthur Hinds (ahinds@cigital.com)"


from xml.dom import minidom
from bs4 import BeautifulSoup
import re
import urllib
import xlsxwriter
import copy

class cveClass:
	def __init__(self):
		pass
	component = ""
	name = ""
	dependency_name = ""
	score = 0.0
	severity = ""
	description = ""
	exploit = False
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
			pass
		except IOError:
			self.exploit = "Undetermined"
			pass

		if len(exploitDoc.find_all(text=re.compile("No results"))) < 1:
			self.exploit = True
			pass
		pass



def main():
	xmldoc = minidom.parse('dependency-check-report.xml')
	dependencies = xmldoc.getElementsByTagName("dependency")
	allcves = []
	print ("Parsing XML Data..  Finding Exploits...  This may take a long time ")
	for dependency in dependencies:
		vulnerabilities = dependency.getElementsByTagName("vulnerability")
		if len(vulnerabilities) > 0:		
			for vulnerability in vulnerabilities:
				tempcve = cveClass()
				tempcve.setName(vulnerability.getElementsByTagName("name")[0].firstChild.data)
				print tempcve.name
				tempcve.setScore(vulnerability.getElementsByTagName("cvssScore")[0].firstChild.data)
				#print vulnerability.getElementsByTagName("cvssScore")[0].firstChild.data
				#print "haha" + str(tempcve.score)
				tempcve.setDescription(vulnerability.getElementsByTagName("description")[0].firstChild.data)
				#print vulnerability.getElementsByTagName("description")[0].firstChild.data
				tempcve.setSeverity(vulnerability.getElementsByTagName("severity")[0].firstChild.data)
				tempcve.setCompnent(dependency.getElementsByTagName("fileName")[0].firstChild.data)
				tempcve.findExploit()
				allcves.append(copy.copy(tempcve))
				#tempcve.toString()

	print ("creating excel")
	workbook = xlsxwriter.Workbook('Dependency-Vulnerabilities.xlsx')
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
		if (cve.exploit):
			worksheet.write(row, 4, "Yes")
		else:
			worksheet.write(row, 4, "No")
		worksheet.write(row, 5, str(cve.description))
		#print cve.description
		row += 1

	workbook.close()

if __name__ == '__main__':
	main()
