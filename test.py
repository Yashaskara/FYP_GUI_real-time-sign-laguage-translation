import json, requests
#from app.arsenal.model.adapter_tools import Adapter_Tools
raw_data_from_url = requests.get("https://developer.walmart.com/image/asdp/us/mp/item/spec/4.0/MP_ITEM_SPEC_4.0.json").json()
pim_property_mappings = []
orderable_properties = []
item_feed_header_properties = []
def generate_adapter_request_payload(adapter_property_name,rule_conditions,schema_rules, data_type,prop_desc,schema_rules_flag=False, required_flag=False):
    pim_property_format = {
        "adapter_property_name": adapter_property_name,
        "required": required_flag,
        "data_type": data_type,
        "description": prop_desc,
        "alias_name": adapter_property_name,
        "is_editable": False,
        "validMetaInfo": True,
    }
    if schema_rules_flag == True:
        pim_property_format.update({"validation_rules": [
            {
                "schema_rules": schema_rules
            }
        ]})
    pim_property_mappings.append(pim_property_format)
def generate_validation_rules(sub_prop_details):
    schema_rules = [None] * 3
    schema_rule_flags = [False] * 3
    flag=0
    # rule number 1
    try:
        schema_rules[flag] = {
            "enum": sub_prop_details["enum"]
        }
        schema_rule_flags[flag] = True
    except:
        schema_rule_flags[flag] = False
    flag+=1
    # rule number 2
    try:
        schema_rules[flag] = {
            "minLength": sub_prop_details["minLength"]
        }
        schema_rule_flags[flag] = True
    except:
        schema_rule_flags[flag] = False
    flag+=1
    # rule number 3
    try:
        schema_rules[flag] = {
            "maxLength": sub_prop_details["maxLength"]
        }
        schema_rule_flags[flag] = True
    except:
        schema_rule_flags[flag] = False
    flag += 1
    # decide if validations rules key should be appended or not
    # count = 0
    # for schema_rule_flag in schema_rule_flags:
    #     if schema_rule_flag == True:
    #         schema_rules.append(schema_rules[count])
    #     count+=1
    if len(schema_rules) == 0:
        return schema_rules, False
    else:
        return schema_rules, True

def extract_property_data(property_data, required_property):
    for property_name in property_data:
        print(property_data[property_name]["type"])
        if property_data[property_name]["type"] == "array" or property_data[property_name]["type"] == "object":
            for property_name_depth in property_data[property_name]["properties"]:
                extract_property_data(property_data[property_name]["properties"][property_name_depth],required_property)
            return
        if property_name in required_property:
            is_required_flag = True
        else: is_required_flag = False
        adapter_property_name = property_data[property_name]["title"]
        schema_rules, schema_rules_flag = generate_validation_rules(property_data[property_name])
        if property_data[property_name]["type"] == "number" or property_data[property_name]["type"] == "integer":
            data_type = "decimal"
        else: data_type = "text"
        prop_desc = property_data[property_name]["title"]
        print(property_name)
        generate_adapter_request_payload(adapter_property_name,'', schema_rules, data_type, prop_desc,schema_rules_flag, is_required_flag)
def collate_orderable_properties():
    orderable_properties_raw_data = raw_data_from_url["properties"]["MPItem"]["items"]["properties"]["Orderable"]["properties"]
    orderable_properties_required_properties = raw_data_from_url["properties"]["MPItem"]["items"]["properties"]["Orderable"]["required"]
    count = 0
    extract_property_data(orderable_properties_raw_data, orderable_properties_required_properties)
    print(pim_property_mappings)
collate_orderable_properties()
#
# count = 0
# for property in raw_data:
#     if property["type"] == "array":
#         if property["items"]["type"] == "object":
#             while (True):
#                 try:
#                     adapter_property_name = list(property["items"]["properties"])[count]
#                 except:
#                     count = 0
#                     break
#                 sub_prop = property["items"]["properties"][adapter_property_name]
#                 data_type = sub_prop["type"]
#                 prop_desc = sub_prop["title"]
#
#                 rule_conditions = []
#                 try:
#                     schema_rules, presence_check = validation_rules_append(sub_prop)
#                 except:
#                     print("nothing" + '\n')
#
#                 if presence_check == False:
#                     property_append(adapter_property_name, None, None, data_type, prop_desc,index_pos)
#                 else:
#                     property_append(adapter_property_name, None, schema_rules, data_type, prop_desc, index_pos)
#                 count = count + 1
#
#
#         else:
#             adapter_property_name = property["title"]
#             rule_conditions = []
#             schema_rules = []
#             data_type = property["items"]["type"]
#             prop_desc = property["title"]
#             property_append(adapter_property_name, rule_conditions, schema_rules, data_type, prop_desc, index_pos)
#     else:
#         adapter_property_name = property["title"]
#         rule_conditions = []
#         schema_rules = []
#         data_type = property["type"]
#         prop_desc = property["title"]
#         property_append(adapter_property_name, rule_conditions, schema_rules, data_type, prop_desc, index_pos)
#
#     # try:
#     #     print("----" + str(list(property["items"]["properties"])[0]) + "\n")
#     # except Exception as e:
#     #     print(e)
#
# # print(json.dumps(pim_property_mappings))
# cred = {"org_id": "internal",
#         "url_prefix": "http://pimqa.unbxd.io/",
#         "un_sso_id": "_un_sso_uid=eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjpudWxsLCJleHBpcnkiOiIyMDIxLTAzLTMxIDA4OjQ2OjMzIFVUQyIsImVtYWlsIjoibmlraGlsLm1pcmFuZGFAdW5ieGQuY29tIiwicmVnaW9ucyI6bnVsbH0.0Zv42EZ7TvZJ9LhyK8PGk8kXqrMuEHgqXjSTZrDXEfQ;"}
#
# Adapter_Tools.create_system_adapter(cred, 'Walmart - Alcoholic Beverages', json.dumps(pim_property_mappings))