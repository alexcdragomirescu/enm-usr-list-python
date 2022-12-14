import re
import xml.etree.ElementTree as ET
from pathlib import Path, PurePath
from openpyxl import Workbook

currentPath = Path(__file__).parent
inputDir = currentPath.joinpath("input")
outputDir = currentPath.joinpath("output")

patterns = {
    'emergency user': [r'^r38148', r'^r38460'],
    'm2m user': [r'\badmi\w+', r'^asbg10', r'^eme-admin', r'\bcscf-\w+', r'^EKMRSTS', r'^adcuser', r'^apran',
                 r'\boss\w+', r'^cacticore', r'^IMSOSS', r'\br\w+', r'^nm_user', r'\bM2M', r'^M2M', r'^m2m', r'\bM2m',
                 r'^M2m', r'^m2m', r'^m2m'],
    'system user': [r'^bsc', r'^eoenmuser', r'^geooperator', r'^fmxamos', r'^fmxenmcli', r'^scripting3', r'^optimanbi',
                    r'^jambala', r'^geouser', r'^tnamuser', r'^pmuser', r'^vnfca', r'^VndDeploy', r'^vMTASuser',
                    r'^syslogadmin'],
    'M-id user': [r'\bA\w+', r'\ba\w+', r'\bM\w+', r'\bm\w+'],
    'signum user': [r'\be\w+', r'\bE\w+', r'\bz\w+', r'\bl\w+', r'^L', r'^Sonu', r'^JesperHJ', r'^pebk', r'^qgioale',
                    r'^teizvzu', r'^qeitaba', r'^SarathSS', r'^thorstenLJ', r'^Je', r'^q'],
    'test user': [r'\btes\w+', r'^t-booss']
}

compiledPatterns = {}
for ok, ov in patterns.items():
    l = []
    for pattern in patterns[ok]:
        l.append(re.compile(pattern))
    compiledPatterns.update({ok: l})

for f in inputDir.iterdir():
    wb = Workbook()
    ws = wb.active
    ws.append(['Username', 'Firstname', 'Surname', 'Email', 'Description', 'Status', 'Roles', 'Usertype'])

    tree = ET.parse(f)
    root = tree.getroot()

    for user in root.findall('user'):
        username = user.find('name').text.rstrip()
        description = user.find('description').text.rstrip() if user.find('description').text else ""
        roles = []
        for pnode in user.findall('privileges/privilege'):
            if pnode != '':
                role = pnode.find('role').text
                roles.append(role)
        roles = sorted(roles)
        roles = ' '.join([str(r) for r in roles])

        searchItems = [username, description]
        userType = ""
        for searchItem in searchItems:
            for ok, ov in compiledPatterns.items():
                for pattern in compiledPatterns[ok]:
                    if re.search(pattern, searchItem):
                        userType = ok
                        break
                if userType != "": break

        ws.append([username, user.find('firstname').text, user.find('surname').text, user.find('email').text, description,
            user.find('status').text, roles, userType])

    wb.save(PurePath(outputDir, f.stem + ".xlsx"))
