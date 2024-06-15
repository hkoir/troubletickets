from rest_framework.serializers import ModelSerializer
from .models import eTicket
from rest_framework import serializers


class eTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = eTicket
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(eTicketSerializer, self).__init__(*args, **kwargs)        
       
        if request and request.method == 'PUT':
            allowed_fields = ['internal_generator_start_time', 'internal_generator_stop_time']
            for field_name in self.fields.keys():
                if field_name not in allowed_fields:
                    self.fields.pop(field_name)

      