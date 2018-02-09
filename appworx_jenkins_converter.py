import argparse
from exp_to_json import exp_to_json
from lxml import etree

parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()
exp_json = exp_to_json(args.file)

project = etree.Element('project')
etree.SubElement(project, 'actions')
etree.SubElement(project, 'description').text = exp_json['so_job_table']['params']['so_job_descr']
properties = etree.SubElement(project, 'properties')

print(etree.tostring(
    project,
    xml_declaration=True,
    encoding='UTF-8',
    pretty_print=True)
)
