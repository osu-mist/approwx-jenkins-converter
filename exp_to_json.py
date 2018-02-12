import re


def exp_to_json(file_path):

    exp_json = {
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
        'O': [],  # logins
        'Q': [],  # queues
        'n': [],  # notifications
        'R': []   # roles
    }
    is_job_table = is_job_prompts = is_object_cond = False

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
                so_soc_order = re.search(r'so_soc_order=([^\s]*)', line).group(1)
                so_obj_type = re.search(r'so_obj_type=([^\s]*)', line).group(1)
                exp_json['so_object_cond'].append({
                    'so_module': so_module,
                    'so_soc_order': so_soc_order,
                    'so_obj_type': so_obj_type,
                    'params': {}
                })
                continue

            # END reset
            if line.startswith('END'):
                is_job_table = is_job_prompts = is_object_cond = False

            match = re.search(r'^(.*?)=(.*)', line)
            if match and is_job_table:
                if match.group(1) == 'roles':
                    exp_json['so_job_table']['params'][match.group(1)] += match.group(2).split()
                else:
                    exp_json['so_job_table']['params'][match.group(1)] = match.group(2)
            elif match and is_job_prompts:
                exp_json['so_job_prompts'][int(so_prompt)-1]['params'][match.group(1)] = match.group(2)
            elif match and is_object_cond:
                exp_json['so_object_cond'][int(so_soc_order)-1]['params'][match.group(1)] = match.group(2)

            # TODO: need to handle line starts with 'DELETE'?

    exp_json['checks'] = check_dict
    return exp_json
