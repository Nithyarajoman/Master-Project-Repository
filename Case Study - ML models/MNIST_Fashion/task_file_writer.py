import ast
import configparser
import math
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import Counter


class Writer:
    """ A base class for DataWriter, MapWriter """
    def __init__(self, root_node_name):
        root_node = ET.Element(root_node_name)
        root_node.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        self.root_node = root_node

    def write_file(self, output_file):
        """ Write the xml file on disk """
        rough_string = ET.tostring(self.root_node, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        data = reparsed.toprettyxml(indent="  ")
        of = open(output_file, 'w')
        of.write(data)
        of.close()

class DataWriter(Writer):
    def __init__(self, mldata):
        super().__init__('data')
        self.mldata = mldata

    def write_data(self, file_name):
        data_types_node = ET.SubElement(self.root_node, 'dataTypes') # Including the header name <datatypes>
        for i, data_type in mldata.types.items():
            self.add_data_type_node(data_types_node, i, data_type)

        tasks_node = ET.SubElement(self.root_node, 'tasks') # Including the header name "<tasks>"
        
        if mldata.tasktype == "count_only":
            prev_mapping = None
            for task_id, values in mldata.task_gen.items():
                gen_count = values['gen_count']
                gen_to_node = values['gen_to']
                gen_type = values['gen_type'] 
                
                ob_req_type  = []
                ob_req_count = []
                task_node = self.add_task_node(tasks_node, task_id)                
            
                if task_id == 0:                        
                    generates_node = self.add_generates_node(task_node)
                    possibility_node = self.add_possibility(generates_node,0,1)
                    destinations_node = self.add_destination_node(possibility_node)
                    if len(gen_to_node)>1:
                        for loop in range(len(gen_to_node)):
                            self.add_destination(destinations_node, loop, (0, 0), 0, gen_count[loop], gen_type[loop], gen_to_node[loop])
                    else:
                        self.add_destination(destinations_node, 0, (0, 0), 0, gen_count, gen_type[0], gen_to_node[0])
                          
                elif task_id == len(mldata.task_gen.items())-1:
                    req_count = prev_mapping['gen_count']
                    req_type = prev_mapping['gen_type']
                    requires_node = self.add_requires_node(task_node)
                    if isinstance(prev_mapping['gen_count'],list):
                        for loop in range(len(req_count)): 
                            self.add_requirement(requires_node, loop, req_type[loop] , loop, req_count[loop])
                    else:
                        self.add_requirement(requires_node, 0, req_type[0] , 0, req_count)
                else:                    
                    requires_node = self.add_requires_node(task_node)
                    for v in mldata.task_gen.values():  
                        if v['gen_to'] != None and len(v['gen_to'])>1:
                            for loop in range(len(v['gen_to'])):                  
                                if task_id == v['gen_to'][loop]:
                                    ob_req_type.append(v['gen_type'][loop])
                                    ob_req_count.append(v['gen_count'][loop])                        
                        else:
                            if v['gen_to'] != None and task_id in v['gen_to']:
                                ob_req_type.append(v['gen_type'][0])
                                ob_req_count.append(v['gen_count'])
                    for loop in range(len(ob_req_type)): 
                        self.add_requirement(requires_node, loop, ob_req_type[loop] , loop, ob_req_count[loop])    
                    
                    generates_node = self.add_generates_node(task_node)
                    possibility_node = self.add_possibility(generates_node, 0, 1)
                    destinations_node = self.add_destination_node(possibility_node)
                    if len(gen_to_node)>1:
                        for loop in range(len(gen_to_node)):
                            self.add_destination(destinations_node, loop, (0, 0), 0, gen_count[loop], gen_type[loop], gen_to_node[loop])
                    else:
                        self.add_destination(destinations_node, 0, (0, 0), 0, gen_count, gen_type[0], gen_to_node[0])
                prev_mapping = values
                  
                            
        else:
            prev_mapping = None
            for task_id, values in mldata.task_repeat.items():
                gen_count = values['gen_count']
                repeat = values['repeat']  
                gen_to_node = values['gen_to']
                gen_type = values['gen_type'] 
                
                ob_req_type  = []
                ob_req_count = []
                task_node = self.add_task_node(tasks_node, task_id, repeat=(repeat,repeat))                
            
                if task_id == 0:                        
                    generates_node = self.add_generates_node(task_node)
                    possibility_node = self.add_possibility(generates_node,0,1)
                    destinations_node = self.add_destination_node(possibility_node)
                    if len(gen_to_node)>1:
                        for loop in range(len(gen_to_node)):
                            self.add_destination(destinations_node, loop, (0, 0), 0, gen_count[loop], gen_type[loop], gen_to_node[loop])
                    else:
                        self.add_destination(destinations_node, 0, (0, 0), 0, gen_count, gen_type[0], gen_to_node[0])
                          
                elif task_id == len(mldata.task_repeat.items())-1:
                    req_count = prev_mapping['gen_count']
                    req_type = prev_mapping['gen_type']
                    requires_node = self.add_requires_node(task_node)
                    if isinstance(prev_mapping['gen_count'],list):
                        for loop in range(len(req_count)): 
                            self.add_requirement(requires_node, loop, req_type[loop] , loop, req_count[loop])
                    else:
                        requires_node = self.add_requires_node(task_node)
                        self.add_requirement(requires_node, 0, req_type[0] , 0, req_count)
                else:                    
                    requires_node = self.add_requires_node(task_node)
                    for v in mldata.task_repeat.values():  
                        if v['gen_to'] != None and len(v['gen_to'])>1:
                            for loop in range(len(v['gen_to'])):                  
                                if task_id == v['gen_to'][loop]:
                                    ob_req_type.append(v['gen_type'][loop])
                                    ob_req_count.append(v['gen_count'][loop])                        
                        else:
                            if v['gen_to'] != None and task_id in v['gen_to']:
                                ob_req_type.append(v['gen_type'][0])
                                ob_req_count.append(v['gen_count'])
                    for loop in range(len(ob_req_type)): 
                        self.add_requirement(requires_node, loop, ob_req_type[loop] , loop, ob_req_count[loop])    
                    
                    generates_node = self.add_generates_node(task_node)
                    possibility_node = self.add_possibility(generates_node, 0, 1)
                    destinations_node = self.add_destination_node(possibility_node)
                    if gen_to_node != None and len(gen_to_node)>1:
                        for loop in range(len(gen_to_node)):
                            self.add_destination(destinations_node, loop, (0, 0), 0, gen_count[loop], gen_type[loop], gen_to_node[loop])
                    else:
                        self.add_destination(destinations_node, 0, (0, 0), 0, gen_count, gen_type[0], gen_to_node[0])
                prev_mapping = values
            
        self.write_file(file_name)

    def add_data_type_node(self, parent_node, id, value):
        data_type_node = ET.SubElement(parent_node, 'dataType')
        data_type_node.set('id', str(id))

        name_node = ET.SubElement(data_type_node, 'name')
        name_node.set('value', value)

    def add_task_node(self, parent_node, t_id, start=(0, 0), duration=(-1, -1), repeat=(1, 1)):
        task_node = ET.SubElement(parent_node, 'task')
        task_node.set('id', str(t_id))

        start_node = ET.SubElement(task_node, 'start')
        start_node.set('min', str(start[0]))
        start_node.set('max', str(start[1]))

        duration_node = ET.SubElement(task_node, 'duration')
        duration_node.set('min', str(duration[0]))
        duration_node.set('max', str(duration[1]))

        repeat_node = ET.SubElement(task_node, 'repeat')
        repeat_node.set('min', str(repeat[0]))
        repeat_node.set('max', str(repeat[1]))

        return task_node

    def add_generates_node(self, parent_node):
        return ET.SubElement(parent_node, 'generates')

    def add_possibility(self, parent_node, id, prob):
        possibility_node = ET.SubElement(parent_node, 'possibility')
        possibility_node.set('id', str(id))

        probability_node = ET.SubElement(possibility_node, 'probability')
        probability_node.set('value', str(prob))
        return possibility_node
        
    def add_destination_node(self, parent_node):
        return ET.SubElement(parent_node, 'destinations')

    def add_destination(self, parent_node, id, delay, interval, count, dt_ix, dist_task):
        destination_node = ET.SubElement(parent_node, 'destination')
        destination_node.set('id', str(id))

        delay_node = ET.SubElement(destination_node, 'delay')
        delay_node.set('min', str(delay[0]))
        delay_node.set('max', str(delay[1]))

        interval_node = ET.SubElement(destination_node, 'interval')
        interval_node.set('min', str(interval))
        interval_node.set('max', str(interval))

        count_node = ET.SubElement(destination_node, 'count')
        count_node.set('min', str(count))
        count_node.set('max', str(count))

        d_type_node = ET.SubElement(destination_node, 'type')
        d_type_node.set('value', str(dt_ix))

        d_task_node = ET.SubElement(destination_node, 'task')
        d_task_node.set('value', str(dist_task))

    def add_requires_node(self, parent_node):
        return ET.SubElement(parent_node, 'requires')

    def add_requirement(self, parent_node, id, type, source, count):
        requirement_node = ET.SubElement(parent_node, 'requirement')
        requirement_node.set('id', str(id))

        d_type_node = ET.SubElement(requirement_node, 'type')
        d_type_node.set('value', str(type))

        source_node = ET.SubElement(requirement_node, 'source')
        source_node.set('value', str(source))

        count_node = ET.SubElement(requirement_node, 'count')
        count_node.set('min', str(count))
        count_node.set('max', str(count))


class MapWriter(Writer):
    def __init__(self, config):
        super().__init__('map')
        self.config = config

    def write_map(self, file_name):
        self.add_bindings(self.config.nodes)

        self.write_file(file_name)

    def add_bindings(self, nodes):
        """
        Binding the tasks with their nodes

        Parameters:
            - tasks: a list of tasks
            - nodes: a list of nodes
        """
        nodes = nodes.values()   
        for t_id, n_id in enumerate(nodes):
            bind_node = ET.SubElement(self.root_node, 'bind')
            task_node = ET.SubElement(bind_node, 'task')
            task_node.set('value', str(t_id))

            node_node = ET.SubElement(bind_node, 'node')
            # the assigned nodes are printed in the map.xml file
            node_node.set('value', str(n_id['Node'])) 
            
            
class Configuration:
    """ The main configuration """

    def __init__(self, path):
        self.path = path
        mldata = configparser.ConfigParser()
        try:
            mldata.read(self.path)
        except Exception:
            raise
        self.types_initial = ast.literal_eval(mldata['Task Description']['types'])
        self.types_count = ast.literal_eval(mldata['Task Description']['datatypes_count'])
        self.basedir = os.getcwd()
        # Parse the dictionary from string representation
        self.tasktype = (mldata['Task Description']['task_type']) 
        self.tasknumbers = int(mldata['Task Description']['tasks_number'])
        self.bitsize = (int(mldata['Task Description']['flitsPerPacket']) * int(mldata['Task Description']['bitWidth']))
        self.size = ast.literal_eval(mldata['ML Statistics']['output_size'])
        self.prob = ast.literal_eval(mldata['ML Statistics']['non_zero_prob'])
        self.out = ast.literal_eval(mldata['ML Statistics']['output_in_bits'])
        self.nodes = ast.literal_eval(mldata['Nodes']['nodes'])   
        
        ############################################################################################
        # to get the separate datatypes when the layer count is complex
        result = {}
        for i in range(self.types_count):
            type_index = i % len(self.types_initial)
            result[str(i)] = self.types_initial[str(type_index)]        
        self.types = result        
        
        ###########################################################################################
        # Code for count alone approach
        self.task_gen = {}
        
        for index,(layer,values) in enumerate(self.nodes.items()):  
            if index < len(self.nodes)-1:       
                for id, key in enumerate(self.prob):
                    sublist = []
                    if index == id:
                        if key in self.out: 
                            if len(values['Generate_to'])>1:
                                if 'Split_percent'in values:
                                    for i in range(len(values['Generate_to'])):
                                        count = (self.prob[key] * self.out[key] * values['Split_percent'][i])
                                        temp = math.ceil(count / self.bitsize)
                                        sublist.append(temp)
                                        task_count = sublist
                                else:
                                    for i in range(len(values['Generate_to'])):
                                        count = (self.prob[key] * self.out[key] * 0.5)
                                        temp = math.ceil(count / self.bitsize)
                                        sublist.append(temp)
                                        task_count = sublist
                            else:
                                if 'Split_percent'in values:
                                    count = (self.prob[key] * self.out[key] * values['Split_percent'][0])
                                else:
                                    count = (self.prob[key] * self.out[key])
                                task_count = math.ceil(count / self.bitsize)
                            self.task_gen[id] = {'gen_count':task_count, 'gen_to':values['Generate_to'], 'gen_type': values['Gen_Types']}
                            j = id
        
        self.task_gen[j+1] = {'gen_count':None, 'gen_to':None, 'gen_type': None}
        print(f'working on part{self.task_gen}')
        ##############################################################################################
        # Code for repeat+count approach 
        self.task_repeat = {}
        for index,(layer,values) in enumerate(self.nodes.items()):
            if index < len(self.nodes)-1:
                for id, key in enumerate(self.prob):                  
                    sublist_cr=[]
                    if index == id:
                        if key in self.size: 
                            layer_size = self.size[key]
                            if isinstance(self.size[key], tuple):
                                # to obtain count
                                if len(values['Generate_to'])>1:
                                    if 'Split_percent'in values:
                                        for i in range(len(values['Generate_to'])):
                                            for i in range(len(values['Generate_to'])):
                                                countcr = (self.prob[key] * self.size[key][-1] * values['Split_percent'][i])
                                            temp = math.ceil(countcr / self.bitsize)
                                            sublist_cr.append(temp)
                                            count_value = sublist_cr
                                    else:
                                        for i in range(len(values['Generate_to'])):
                                            for i in range(len(values['Generate_to'])):
                                                countcr = (self.prob[key] * self.size[key][-1] * 0.5)
                                            temp = math.ceil(countcr / self.bitsize)
                                            sublist_cr.append(temp)
                                            count_value = sublist_cr   
                                else:
                                    if 'Split_percent'in values:
                                        countcr = (self.prob[key] * self.size[key][-1] * 32 * values['Split_percent'][0])
                                    else:
                                        countcr = (self.prob[key] * self.size[key][-1] * 32)
                                    count_value = math.ceil(countcr / self.bitsize)
                                # to obtain repeat    
                                if(len(layer_size) == 4):
                                    repeat_value = math.ceil(self.size[key][1] * self.size[key][2])
                                else:
                                    repeat_value = 1
                            elif isinstance(self.size[key], list):
                                # to obtain count
                                if len(values['Generate_to'])>1:
                                    for i in range(len(values['Generate_to'])):
                                        for i in range(len(values['Generate_to'])):
                                            countcr = (self.size[key][0][-1] * self.prob[key] * values['Split_percent'][i])
                                        temp = math.ceil(countcr / self.bitsize)
                                        sublist_cr.append(temp)
                                        count_value = sublist_cr
                                        
                                else:
                                    if 'Split_percent'in values:
                                        countcr = (self.size[key][0][-1] * self.prob[key] * 32 * values['Split_percent'][0])
                                    else:
                                        countcr = (self.size[key][0][-1] * self.prob[key] * 32)
                                    count_value = math.ceil(countcr / self.bitsize)
                                # to obtain repeat    
                                if(len(layer_size[0]) == 4):
                                    repeat_value = math.ceil(self.size[key][0][1] * self.size[key][0][2])
                                else:
                                    repeat_value = 1 
                            self.task_repeat[id] = {'gen_count':count_value,'repeat': repeat_value, 'gen_to':values['Generate_to'], 'gen_type': values['Gen_Types']}
                            j = id
        
        self.task_repeat[j+1] = {'gen_count':None,'repeat': 1, 'gen_to':None, 'gen_type': None}   
        print(f'task_repeat is {self.task_repeat}')
        ##############################################################################################        
        
        
if __name__ == '__main__':
    mldata = Configuration('mldata.ini')
    
    data_writer = DataWriter(mldata)
    data_writer.write_data('data.xml')
    map_writer = MapWriter(mldata)
    map_writer.write_map('map.xml')

