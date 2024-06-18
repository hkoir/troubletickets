from django.contrib import admin

from .models import ChatMessage,eTicket,ChildTicket,ChildTicketExternal


admin.site.register(ChatMessage)
admin.site.register(eTicket)
admin.site.register(ChildTicket)
admin.site.register(ChildTicketExternal)



