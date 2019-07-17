# -*- coding:utf-8 -*-

import boto3

session = boto3.session.Session(region_name='cn-north-1')
client = session.client('ec2')

class aws_tag(object):

    def find_target(self,service_type):                      #列出所有相关服务的列表，（例如所有卷的列表）
        if service_type == "NetworkInterfaces":
         response = client.describe_network_interfaces(                
            Filters=[
                {
                   'Name': 'status',
                   'Values': [
                       'in-use',
                    ]
                },
            ],
            )
        elif  service_type == "Volumes":
                response = client.describe_volumes(                
                Filters=[
                {
                   'Name': 'status',
                   'Values': [
                       'in-use',
                    ]
                },
            ],
            )
        elif service_type == "Snapshots":
            response = client.describe_snapshots(
                Filters=[
                    {
                        'Name': 'status',
                        'Values': [
                            'completed',
                        ]
                    },
                ],
    
            )

        else:
         print ("Unkown service_type)")

        return response

    def Des_all_tag(self,Target_id):
        response = client.describe_tags(
        Filters=[
            {
                'Name': 'resource-id',
                'Values': [
                    Target_id,
                ]
            },
        ],
        )
        return response

    def Find_tag_kv(self,response_ec2):       #根据服务ID（例如卷id）找到相关联的EC2实例的所有tag的key和value
        Ec2_key = []
        Ec2_key_Value = []
        Atag = ['org','Name','operatingsystem','ClusterIdentifier','ClusterType','owner']
        for e in (response_ec2['Tags']):
            if e['Key'] in Atag:                                       
                Ec2_key.append(e['Key'])
                Ec2_key_Value.append(e['Value'])
                K_V = dict(zip(Ec2_key,Ec2_key_Value))
        if 'K_V' not in locals():
            K_V = {'org':'','Name':'','operatingsystem':'','ClusterIdentifier':'','ClusterType':'','owner':''}           
        return K_V

   # @retry()
    def Create_tag(self,resource_id,keystr,valuestr):
        try:
            response = client.create_tags(
                DryRun=False,
                Resources=[                                                               
                    resource_id,
                ],
                Tags=[
                    {
                       'Key': keystr,
                        'Value': valuestr,
                    },
                ],
                )
            print("create tag \"%s=%s\" for resource %s" % (keystr,valuestr,resource_id))    
        except:
            print ("Error:Can't createtag \"%s=%s\" for resource %s" % (keystr,valuestr,resource_id))

    def NetworkInterfaces_tag(self):                  #将关联的EC2实例的tag覆盖到此服务
        response = self.find_target("NetworkInterfaces")
        for Attr in  response['NetworkInterfaces']:
            if ('InstanceId' in Attr['Attachment']):
                response_ec2 = self.Des_all_tag(Attr['Attachment']['InstanceId'])
                K_V = self.Find_tag_kv(response_ec2)          
                for New_key in K_V:
                    self.Create_tag(Attr['NetworkInterfaceId'],New_key,K_V[New_key])

    def Volume_tag(self):                                    #将关联的EC2实例的tag覆盖到此服务
        response = self.find_target("Volumes")
        for Attr in response['Volumes']:                                                  
            response_ec2 = self.Des_all_tag(Attr['Attachments'][0]['InstanceId'])
            K_V = self.Find_tag_kv(response_ec2)
            for New_key in K_V:
                self.Create_tag(Attr['Attachments'][0]['VolumeId'],New_key,K_V[New_key])

    def Snapshot_tag(self):
        response = self.find_target("Snapshots")
        for Attr in response['Snapshots']:
            if 'Tags' in Attr:
                for ex_Attr in Attr['Tags']:
                    if "creator" in ex_Attr.values():
                        response_ec2 = self.Des_all_tag(Attr['VolumeId'])
                        if response_ec2['Tags']:
                            K_V = self.Find_tag_kv(response_ec2)
                            for New_key in K_V:
                                self.Create_tag(Attr['SnapshotId'],New_key,K_V[New_key])

if __name__ == '__main__':
        demo = aws_tag()
        print ("NetworkInterfaces progress:")
        demo.NetworkInterfaces_tag()
        print ("Volumes progress:")
        demo.Volume_tag()
        print ("Snapshots progress:")
        demo.Snapshot_tag()
        print ("All Done!!!")
