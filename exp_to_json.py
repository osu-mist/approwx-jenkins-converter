import re
import json


def exp_to_json(file_path):

    exp_json = {
        'aw_module_sched': [],
        'so_job_table': {},
        'so_job_prompts': [],
        'so_object_cond': []
    }
    check_dict = {
        'B': [],  # program types
        'D': [],  # data type
        'G': [],  # agents
        'K': [],  # application
        'L': [],  # pathes
        'M': [],  #
        'O': [],  # logins
        'Q': [],  # queues
        'n': [],  # notifications
        'R': [],  # roles
        'U': []   #
    }

    is_job_table = False
    is_documentation = False
    is_module_sched = False
    module_sched_idx = -1
    is_job_prompts = False
    is_object_cond = False

    with open(file_path, 'r') as f:

        for line in f:
            if line.startswith('CHECK'):
                match = re.search(r'^CHECK (.*) (.*)', line)
                check_dict[match.group(1)].append(match.group(2))

            # so_job_table
            if line.startswith('START=so_job_table'):
                is_job_table = True
                so_module = re.search(r'so_module=([^\s]*)', line).group(1)
                exp_json['so_job_table'] = {
                    'so_module': so_module,
                    'params': {'roles': []}
                }
                continue

            # so_documentation
            if line.startswith('START=so_documentation'):
                is_documentation = True
                so_module = re.search(r'so_module=([^\s]*)', line).group(1)
                so_doc_source = re.search(r'so_doc_source=([^\s]*)', line).group(1)
                so_doc_type = re.search(r'so_doc_type=([^\s]*)', line).group(1)
                exp_json['so_documentation'] = {
                    'so_module': so_module,
                    'so_doc_source': so_doc_source,
                    'so_doc_type': so_doc_type,
                    'so_doc_text': ''
                }
                continue

            # aw_module_sched
            if line.startswith('START=aw_module_sched'):
                is_module_sched = True
                module_sched_idx += 1
                so_module = re.search(r'so_module=([^\s]*)', line).group(1)
                aw_sch_name = re.search(r'aw_sch_name=([^\s]*)', line).group(1)
                exp_json['aw_module_sched'].append({
                    'so_module': so_module,
                    'aw_sch_name': aw_sch_name,
                    'params': {}
                })
                continue

            # so_job_prompts
            if line.startswith('START=so_job_prompts'):
                is_job_prompts = True
                so_module = re.search(r'so_module=([^\s]*)', line).group(1)
                so_prompt = re.search(r'so_prompt=([^\s]*)', line).group(1)
                exp_json['so_job_prompts'].append({
                    'so_module': so_module,
                    'so_prompt': so_prompt,
                    'params': {}
                })
                continue

            # so_object_cond
            if line.startswith('START=so_object_cond'):
                is_object_cond = True
                so_module = re.search(r'so_module=([^\s]*)', line).group(1)
                # so_soc_order = re.search(r'so_soc_order=([^\s]*)', line).group(1)
                # so_obj_type = re.search(r'so_obj_type=([^\s]*)', line).group(1)
                # exp_json['so_object_cond'].append({
                #     'so_module': so_module,
                #     'so_soc_order': so_soc_order,
                #     'so_obj_type': so_obj_type,
                #     'params': {}
                # })
                continue

            # END reset
            if line.startswith('END'):
                is_job_table = False
                is_documentation = False
                is_module_sched = False
                is_job_prompts = False
                is_object_cond = False

            match = re.search(r'^(.*?)=(.*)', line)
            if match and is_job_table:
                if match.group(1) == 'roles':
                    exp_json['so_job_table']['params'][match.group(1)] += match.group(2).split()
                else:
                    exp_json['so_job_table']['params'][match.group(1)] = match.group(2)
            elif match and is_documentation:
                exp_json['so_documentation']['so_doc_text'] += match.group(2)
            elif match and is_module_sched:
                exp_json['aw_module_sched'][module_sched_idx]['params'][match.group(1)] = match.group(2)
            elif match and is_job_prompts:
                exp_json['so_job_prompts'][int(so_prompt)-1]['params'][match.group(1)] = match.group(2)
            # elif match and is_object_cond:
            #     exp_json['so_object_cond'][int(so_soc_order)-1]['params'][match.group(1)] = match.group(2)

            # TODO: need to handle line starts with 'DELETE'?

    exp_json['checks'] = check_dict
    print(json.dumps(exp_json, indent=4))
    return exp_json
