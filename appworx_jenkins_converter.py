import argparse
import jenkins
from exp_to_json import exp_to_json
from lxml import etree as et


def set_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("exp_file")
    parser.add_argument("jenkins_url")
    parser.add_argument("jenkins_username")
    parser.add_argument("jenkins_token")
    return parser.parse_args()


def initial_project():
    global properties, builders, publishers, buildWrappers

    et.SubElement(project, 'description').text = exp_json['so_job_table']['params']['so_job_descr']
    et.SubElement(project, 'actions')
    et.SubElement(project, 'canRoam').text = 'true'
    et.SubElement(project, 'keepDependencies').text = 'false'
    et.SubElement(project, 'disabled').text = 'false'
    et.SubElement(project, 'blockBuildWhenUpstreamBuilding').text = 'false'
    et.SubElement(project, 'concurrentBuild').text = 'false'
    et.SubElement(project, 'scm', attrib={"class": "jenkins.scm.NullSCM"})
    et.SubElement(project, 'triggers', attrib={"class": "vector"})
    properties = et.SubElement(project, 'properties')

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


if __name__ == '__main__':
    args = set_arguments()
    exp_json = exp_to_json(args.exp_file)

    # convert AppWorx module/job to Jenkins job project
    if not exp_json['so_chain_detail']:
        project = et.Element('project')
        initial_project()

        # build steps
        if exp_json['so_job_table']['params']['so_program']:
            shell = et.SubElement(builders, 'hudson.tasks.Shell')
        et.SubElement(shell, 'command').text = 'sqr {}.sqr'.format(exp_json['so_job_table']['params']['so_program'])

    # convert AppWorx chain/process flow to Jenkins multijob project
    else:
        project = et.Element('com.tikal.jenkins.plugins.multijob.MultiJobProject', plugin='jenkins-multijob-plugin@1.29')
        initial_project()

    jenkins_job_config = et.tostring(
        project,
        xml_declaration=True,
        encoding='UTF-8',
        pretty_print=True
    )

    print(jenkins_job_config)
    # import config directly to Jenkins
    # server = jenkins.Jenkins(
    #     args.jenkins_url,
    #     username=args.jenkins_username,
    #     password=args.jenkins_token
    # )
    # server.create_job(exp_json['so_job_table']['so_module'], jenkins_job_config)
