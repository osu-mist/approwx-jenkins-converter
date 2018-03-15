import argparse
import jenkins
import json
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

    rebuilds = et.SubElement(
        properties,
        'com.sonyericsson.rebuild.RebuildSettings',
        plugin='rebuild@1.27'
    )
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

    # ******************************************************
    # create phases topology
    # ******************************************************
    original = [(job['params']['so_predecessors'], job['so_task_name']) for job in exp_json['so_chain_detail']]
    phases = [[] for _ in range(len(original))]
    while original:
        for job in original:
            so_predecessors, so_task_name = job
            if not so_predecessors:
                phases[0].append(so_task_name)
                original.remove(job)
            elif so_predecessors in phases:
                phases[phases.index(so_predecessors) + 1].append(so_task_name)
                original.remove(job)
            elif len(so_predecessors) > 1:
                for phase in phases:
                    if so_predecessors[0] in phase:
                        phases[phases.index(phase) + 1].append(so_task_name)
                        original.remove(job)

    # ******************************************************
    # AppWorx module (job) to Jenkins free-style job project
    # ******************************************************
    if not exp_json['so_chain_detail']:
        project = et.Element('project')
        initial_project()

        # build steps
        # *** only run sqr file for the demo ***
        so_program = exp_json['so_job_table']['params']['so_program']
        if so_program:
            shell = et.SubElement(builders, 'hudson.tasks.Shell')
            et.SubElement(shell, 'command').text = 'sqr {}.sqr'.format(so_program)

    # ********************************************************
    # AppWorx chain (process flow) to Jenkins multijob project
    # ********************************************************
    else:
        project = et.Element(
            'com.tikal.jenkins.plugins.multijob.MultiJobProject',
            plugin='jenkins-multijob-plugin@1.29'
        )
        initial_project()

        # build steps
        chain_detail = sorted(exp_json['so_chain_detail'], key=lambda x: x['params']['so_chain_order'])
        for index, chain_phase in enumerate(chain_detail):
            phase = et.SubElement(builders, 'com.tikal.jenkins.plugins.multijob.MultiJobBuilder')
            et.SubElement(phase, 'phaseName').text = 'Phase {}'.format(index + 1)
            et.SubElement(phase, 'continuationCondition').text = 'ALWAYS'
            et.SubElement(phase, 'executionType').text = 'PARALLEL'
            phase_jobs = et.SubElement(phase, 'phaseJobs')

            # jobs in each phase
            phase_job = et.SubElement(phase_jobs, 'com.tikal.jenkins.plugins.multijob.PhaseJobsConfig')
            et.SubElement(phase_job, 'jobName').text = chain_phase['params']['so_module']
            et.SubElement(phase_job, 'currParams').text = 'true'
            et.SubElement(phase_job, 'aggregatedTestResults').text = 'false'
            et.SubElement(phase_job, 'exposedSCM').text = 'false'
            et.SubElement(phase_job, 'disableJob').text = 'false'
            et.SubElement(phase_job, 'parsingRulesPath')
            et.SubElement(phase_job, 'maxRetries').text = '0'
            et.SubElement(phase_job, 'enableRetryStrategy').text = 'false'
            et.SubElement(phase_job, 'enableCondition').text = 'false'
            et.SubElement(phase_job, 'abortAllJob').text = 'true'
            et.SubElement(phase_job, 'config', attrib={"class": "empty-list"})
            et.SubElement(phase_job, 'killPhaseOnJobResultCondition').text = 'FAILURE'
            et.SubElement(phase_job, 'buildOnlyIfSCMChanges').text = 'false'
            et.SubElement(phase_job, 'applyConditionOnlyIfNoSCMChanges').text = 'false'

            if chain_phase['so_task_name'] in exp_json['so_object_cond']:

                # *** only create condition text for the demo ***
                condition_text = []
                conditions = exp_json['so_object_cond'][chain_phase['so_task_name']]['conditions']
                for condition in conditions:
                    so_condition_1 = condition['so_condition_1']
                    so_qualifier = condition['so_qualifier']
                    so_condition_2 = condition['so_condition_2']
                    sub_condition = '({} {} {})'.format(so_condition_1, so_qualifier, so_condition_2)
                    condition_text.append(sub_condition)

                et.SubElement(phase_job, 'enableCondition').text = 'true'
                et.SubElement(phase_job, 'condition').text = ' && '.join(condition_text)
            else:
                et.SubElement(phase_job, 'condition')

    # export Jenkins config file
    jenkins_job_config = et.tostring(
        project,
        xml_declaration=True,
        encoding='UTF-8',
        pretty_print=True
    )

    # print(jenkins_job_config)
    # import config directly to Jenkins
    # server = jenkins.Jenkins(
    #     args.jenkins_url,
    #     username=args.jenkins_username,
    #     password=args.jenkins_token
    # )
    # server.create_job(exp_json['so_job_table']['so_module'], jenkins_job_config)
