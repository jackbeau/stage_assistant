# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import service_pb2 as service__pb2

GRPC_GENERATED_VERSION = '1.64.0'
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = '1.65.0'
SCHEDULED_RELEASE_DATE = 'June 25, 2024'
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in service_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
        + f' This warning will become an error in {EXPECTED_ERROR_RELEASE},'
        + f' scheduled for release on {SCHEDULED_RELEASE_DATE}.',
        RuntimeWarning
    )


class ScriptServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.AddMargin = channel.unary_unary(
                '/ScriptService/AddMargin',
                request_serializer=service__pb2.AddMarginRequest.SerializeToString,
                response_deserializer=service__pb2.AddMarginResponse.FromString,
                _registered_method=True)
        self.PerformOCR = channel.unary_unary(
                '/ScriptService/PerformOCR',
                request_serializer=service__pb2.OCRRequest.SerializeToString,
                response_deserializer=service__pb2.OCRResponse.FromString,
                _registered_method=True)
        self.StartSpeechToScriptPointer = channel.unary_unary(
                '/ScriptService/StartSpeechToScriptPointer',
                request_serializer=service__pb2.StartRequest.SerializeToString,
                response_deserializer=service__pb2.StartResponse.FromString,
                _registered_method=True)
        self.StopSpeechToScriptPointer = channel.unary_unary(
                '/ScriptService/StopSpeechToScriptPointer',
                request_serializer=service__pb2.StopRequest.SerializeToString,
                response_deserializer=service__pb2.StopResponse.FromString,
                _registered_method=True)
        self.StartPerformerTracker = channel.unary_unary(
                '/ScriptService/StartPerformerTracker',
                request_serializer=service__pb2.StartRequest.SerializeToString,
                response_deserializer=service__pb2.StartResponse.FromString,
                _registered_method=True)
        self.StopPerformerTracker = channel.unary_unary(
                '/ScriptService/StopPerformerTracker',
                request_serializer=service__pb2.StopRequest.SerializeToString,
                response_deserializer=service__pb2.StopResponse.FromString,
                _registered_method=True)
        self.GetStatuses = channel.unary_unary(
                '/ScriptService/GetStatuses',
                request_serializer=service__pb2.StatusRequest.SerializeToString,
                response_deserializer=service__pb2.StatusResponse.FromString,
                _registered_method=True)


class ScriptServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def AddMargin(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PerformOCR(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartSpeechToScriptPointer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StopSpeechToScriptPointer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartPerformerTracker(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StopPerformerTracker(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStatuses(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ScriptServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'AddMargin': grpc.unary_unary_rpc_method_handler(
                    servicer.AddMargin,
                    request_deserializer=service__pb2.AddMarginRequest.FromString,
                    response_serializer=service__pb2.AddMarginResponse.SerializeToString,
            ),
            'PerformOCR': grpc.unary_unary_rpc_method_handler(
                    servicer.PerformOCR,
                    request_deserializer=service__pb2.OCRRequest.FromString,
                    response_serializer=service__pb2.OCRResponse.SerializeToString,
            ),
            'StartSpeechToScriptPointer': grpc.unary_unary_rpc_method_handler(
                    servicer.StartSpeechToScriptPointer,
                    request_deserializer=service__pb2.StartRequest.FromString,
                    response_serializer=service__pb2.StartResponse.SerializeToString,
            ),
            'StopSpeechToScriptPointer': grpc.unary_unary_rpc_method_handler(
                    servicer.StopSpeechToScriptPointer,
                    request_deserializer=service__pb2.StopRequest.FromString,
                    response_serializer=service__pb2.StopResponse.SerializeToString,
            ),
            'StartPerformerTracker': grpc.unary_unary_rpc_method_handler(
                    servicer.StartPerformerTracker,
                    request_deserializer=service__pb2.StartRequest.FromString,
                    response_serializer=service__pb2.StartResponse.SerializeToString,
            ),
            'StopPerformerTracker': grpc.unary_unary_rpc_method_handler(
                    servicer.StopPerformerTracker,
                    request_deserializer=service__pb2.StopRequest.FromString,
                    response_serializer=service__pb2.StopResponse.SerializeToString,
            ),
            'GetStatuses': grpc.unary_unary_rpc_method_handler(
                    servicer.GetStatuses,
                    request_deserializer=service__pb2.StatusRequest.FromString,
                    response_serializer=service__pb2.StatusResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ScriptService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ScriptService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ScriptService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def AddMargin(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ScriptService/AddMargin',
            service__pb2.AddMarginRequest.SerializeToString,
            service__pb2.AddMarginResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def PerformOCR(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ScriptService/PerformOCR',
            service__pb2.OCRRequest.SerializeToString,
            service__pb2.OCRResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StartSpeechToScriptPointer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ScriptService/StartSpeechToScriptPointer',
            service__pb2.StartRequest.SerializeToString,
            service__pb2.StartResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StopSpeechToScriptPointer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ScriptService/StopSpeechToScriptPointer',
            service__pb2.StopRequest.SerializeToString,
            service__pb2.StopResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StartPerformerTracker(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ScriptService/StartPerformerTracker',
            service__pb2.StartRequest.SerializeToString,
            service__pb2.StartResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def StopPerformerTracker(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ScriptService/StopPerformerTracker',
            service__pb2.StopRequest.SerializeToString,
            service__pb2.StopResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetStatuses(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ScriptService/GetStatuses',
            service__pb2.StatusRequest.SerializeToString,
            service__pb2.StatusResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
