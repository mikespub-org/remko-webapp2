from protorpc import messages, remote


class BonjourRequest(messages.Message):
    my_name = messages.StringField(1, required=True)


class BonjourResponse(messages.Message):
    hello = messages.StringField(1, required=True)


class BonjourService(remote.Service):
    @remote.method(BonjourRequest, BonjourResponse)
    def bonjour(self, request):
        return BonjourResponse(hello=f"Bonjour, {request.my_name}!")


class CiaoRequest(messages.Message):
    my_name = messages.StringField(1, required=True)


class CiaoResponse(messages.Message):
    hello = messages.StringField(1, required=True)


class CiaoService(remote.Service):
    @remote.method(CiaoRequest, CiaoResponse)
    def ciao(self, request):
        return CiaoResponse(hello=f"Ciao, {request.my_name}!")
