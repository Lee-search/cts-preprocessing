import xml.etree.ElementTree as ET
import re
from tqdm import tqdm

from External_methods import pretty_print, create_directory

# ---- Internal Methods ---- #
# criteria_separation: In/Ex Criteria 항목을 분류해서 리턴
# XML_preprocessing: XML 파일리스트를 받아와서 전처리 후 새로운 파일로 저장
def criteria_separation(criteria,count,doc_id):
    
    criteria_lower = criteria.lower()

    # 정규식에 해당하는 내용이 있으면 RegexObj, 없으면 NoneObj 리턴
    both = re.compile("inclusion/exclusion criteria:").search(criteria_lower)
    include = re.compile("inclusion criteria").search(criteria_lower)
    exclude = re.compile("exclusion criteria").search(criteria_lower)
    
    include_s = re.compile("inclusion").search(criteria_lower)
    exclude_s = re.compile("exclusion").search(criteria_lower)
    
    in_text,ex_text = '',''
    
    # 같이 나오는 경우, 예외로 둘다 저장
    if both:
        #print(f"Info: Inclusion/Exclusion is Found. {doc_id}")
        
        # Inclusion's Start Point
        include_sp = both.end()
        
        in_text = criteria[include_sp:]
        ex_text = in_text
    
    # 둘 다 있을 경우,
    elif include and exclude:
        # Inclusion's Start Point
        include_sp = include.end()
        # Inclusion's End Point & Exclusion's Start Point
        include_ep = exclude.start()
        exclude_sp = exclude.end()
        
        in_text = criteria[include_sp:include_ep]
        ex_text = criteria[exclude_sp:]

    # Inclusion 만 있는 경우,
    elif include:
        # Inclusion's Start Point
        include_sp = include.end()
        in_text = criteria[include_sp:]

    # Exclusion 만 있는 경우,
    elif exclude:
        exclude_sp = exclude.end()
        ex_text = criteria[exclude_sp:]
    else:
        if include_s and exclude_s:
            # Inclusion's Start Point
            include_sp = include_s.end()
            # Inclusion's End Point & Exclusion's Start Point
            include_ep = exclude_s.start()
            exclude_sp = exclude_s.end()
        
            in_text = criteria[include_sp:include_ep]
            ex_text = criteria[exclude_sp:]

        elif include_s:
            # Inclusion's Start Point
            include_sp = include_s.end()
            in_text = criteria[include_sp:]

        elif exclude_s:
            exclude_sp = exclude_s.end()
            ex_text = criteria[exclude_sp:]
            
        # 해당하는 정규식이 없는 경우, 예외로 둘 다 기존 Criteria 저장
        else:
            count += 1
            in_text = criteria
            ex_text = in_text
    
    # In. Criteria, Ex. Criteria, Count of NaN
    return in_text, ex_text, count

def XML_preprocessing(input_file, output_file):
    
    file_list = input_file

    total_count = 0
    count_of_NaN = 0

    with open(file_list, 'r', encoding = 'utf-8') as filelist:
        for file in tqdm(filelist):
            # 파일 경로 유도
            f = file.strip('\n')
            f = f[1:]
            f = "/home2/TREC_collections/TREC-CT" + f
            
            xml_file = open(f, 'rt', encoding='UTF8')
            
            root = ET.parse(xml_file).getroot()

            description = ""
            brief_summary = ""
            criteria = ""
            condition = ""
            gender = ""
            minimum_age = ""
            maximum_age = ""
            
            total_count += 1

            # XML 태그에서 텍스트 추출

            try:
                # doc_id, title are Always in it.
                doc_id = root.find('id_info').find('nct_id').text
                title = root.find('brief_title').text
                
                # Other fields are not sure.
                if root.find('brief_summary') is not None:
                    summary = root.find('brief_summary').find('textblock').text
                    
                if root.find('detailed_description') is not None:
                    description = root.find('detailed_description').find('textblock').text
                
                finder = root.find('eligibility')
                if (finder and root.find('eligibility').find('criteria')) is not None:
                    criteria = root.find('eligibility').find('criteria').find('textblock').text
                    
                #if root.findall('intervention'):
                #    for inv in root.findall('intervention'):
                #    intervention_type = root.find('intervention').find('intervention_type').text
                #    intervention_name = root.find('intervention').find('intervention_name').text
                    
                if root.find('condition') is not None:
                    condition = root.find('condition').text
                
                if (finder and finder.find('gender')) is not None:
                    gender = root.find('eligibility').find('gender').text
                    
                if (finder and finder.find('minimum_age')) is not None:
                    minimum_age = root.find('eligibility').find('minimum_age').text
                
                if (finder and finder.find('maximum_age')) is not None:
                    maximum_age = root.find('eligibility').find('maximum_age').text
                
            except KeyError:
                print("Error: Failed to load XML section.")

            if total_count%50000 == 0:
                print(f'{total_count}: Doc_id is {doc_id}\n')

            # Inclusion/Exclusion 분리
            inclusion_criteria, exclusion_criteria, count_of_NaN = criteria_separation(criteria, count_of_NaN, doc_id)

            # XML 파일 생성
            out_root = ET.Element("clinical_study")

            t_doc_id = ET.Element("nct_id")
            t_doc_id.text = doc_id
            out_root.append(t_doc_id)

            t_title = ET.Element("brief_title")
            t_title.text = title
            out_root.append(t_title)

            t_summary = ET.Element("brief_summary")
            t_summary.text = summary
            out_root.append(t_summary)

            t_description = ET.Element("detailed_description")
            t_description.text = description
            out_root.append(t_description)
            
            #t_intervention_type = ET.Element("intervention_type")
            #t_intervention_type.text = intervention_type
            #out_root.append(t_intervention_type)
            
            #t_intervention_name = ET.Element("intervention_name")
            #t_intervention_name.text = intervention_name
            #out_root.append(t_intervention_type)

            t_condition = ET.Element("condition")
            t_condition.text = condition
            out_root.append(t_condition)
            
            t_gender = ET.Element("gender")
            t_gender.text = gender
            out_root.append(t_gender)
            
            t_minimum_age = ET.Element("minimum_age")
            min_age = re.sub(r'[^0-9]', '', minimum_age)
            if min_age == '':
                min_age = '0'
            t_minimum_age.text = min_age
            out_root.append(t_minimum_age)
            
            t_maximum_age = ET.Element("maximum_age")
            max_age = re.sub(r'[^0-9]', '', maximum_age)
            if max_age == '':
                max_age = '100'
            t_maximum_age.text = max_age
            out_root.append(t_maximum_age)
            
            t_criteria = ET.Element("criteria")
            t_inclusion_criteria = ET.Element("inclusion_criteria")
            t_exclusion_criteria = ET.Element("exclusion_criteria")

            t_criteria.text = criteria
            if inclusion_criteria != exclusion_criteria:
                t_inclusion_criteria.text = inclusion_criteria
                t_exclusion_criteria.text = exclusion_criteria
                
            out_root.append(t_inclusion_criteria)
            out_root.append(t_exclusion_criteria)
            out_root.append(t_criteria)
            
            # XML 형식에 맞춰 저장
            pretty_print(out_root)

            tree = ET.ElementTree(out_root)

            file_name = output_file + '/' + file.strip('\n')[2:-15]
            create_directory(file_name)
            with open(file_name + doc_id + '.xml', "wb") as file:
                tree.write(file, encoding='utf-8', xml_declaration=True)
                
    print(f"Total Documents Count: {total_count}")
    print(f"Criteria Not Exist: {count_of_NaN}")