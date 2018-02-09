import argparse
import json
from exp_to_json import exp_to_json
from lxml import etree as et

parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()
exp_json = exp_to_json(args.file)

# initiate template
project = et.Element('project')
et.SubElement(project, 'description').text = exp_json['so_job_table']['params']['so_job_descr']
et.SubElement(project, 'actions')
et.SubElement(project, 'canRoam').text = 'true'
et.SubElement(project, 'keepDependencies').text = 'false'
et.SubElement(project, 'disabled').text = 'false'
et.SubElement(project, 'blockBuildWhenUpstreamBuilding').text = 'false'
et.SubElement(project, 'concurrentBuild').text = 'false'

scm = et.SubElement(project, 'scm', attrib={"class": "jenkins.scm.NullSCM"})
triggers = et.SubElement(project, 'triggers', attrib={"class": "vector"})
properties = et.SubElement(project, 'properties')

# RebuildSettings
rebuilds = et.SubElement(properties, 'com.sonyericsson.rebuild.RebuildSettings', plugin='rebuild@1.27')
et.SubElement(rebuilds, 'autoRebuild').text = 'false'
et.SubElement(rebuilds, 'rebuildDisabled').text = 'false'

builders = et.SubElement(project, 'builders')
publishers = et.SubElement(project, 'publishers')
buildWrappers = et.SubElement(project, 'buildWrappers')

# paramterized job
if exp_json['so_job_prompts']:
    pdp = et.SubElement(properties, 'hudson.model.ParametersDefinitionProperty')
    pd = et.SubElement(pdp, 'parameterDefinitions')
    for prompt in exp_json['so_job_prompts']:
        spd = et.SubElement(pd, 'hudson.model.StringParameterDefinition')
        et.SubElement(spd, 'name').text = prompt['params']['so_prompt_descr']
        et.SubElement(spd, 'description')
        et.SubElement(spd, 'defaultValue').text = prompt['params']['so_prompt_dflt']
        et.SubElement(spd, 'trim').text = 'false'

# build steps
if exp_json['so_job_table']['params']['so_program']:
    shell = et.SubElement(builders, 'hudson.tasks.Shell')
    et.SubElement(shell, 'command').text = 'sqr {}.sqr'.format(exp_json['so_job_table']['params']['so_program'])


print(et.tostring(
    project,
    xml_declaration=True,
    encoding='UTF-8',
    pretty_print=True)
)
