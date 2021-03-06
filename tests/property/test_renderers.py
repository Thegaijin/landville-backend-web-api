from collections import OrderedDict
import json

from rest_framework.exceptions import ErrorDetail

from tests.property import BaseTest
from property.serializers import PropertySerializer
from property.renderers import PropertyJSONRenderer


class PropertyJSONRendererTest(BaseTest):
    """Define unit tests for the PropertyJSONRenderer"""

    def test_that_renderer_properly_renders_property_dictionary_data(self):

        serializer = PropertySerializer(
            data=self.property_data)
        serializer.is_valid()
        payload = serializer.data
        payload['id'] = self.property2.pk
        response = {"data": {"property": payload}}
        rendered_property = self.property_renderer.render(response)
        self.assertIn("property", rendered_property)
        # the fields with choices are rendered with human-readable values
        self.assertIn("Building", rendered_property)

    def test_that_errors_are_rendered_as_expected(self):
        dict_data = {"errors": "This error should be properly rendered"
                     }
        rendered_data = json.loads(self.property_renderer.render(dict_data))
        expected_data = {"errors": "This error should be properly rendered"}
        self.assertEqual(rendered_data, expected_data)

    def test_errors_with_no_errors_key_are_properly_rendered(self):
        """
        There are instances where errors are passed on without
        being wrapped in an `errors` key. This can cause the renderer
        to crash because they are not caught when we try to get the error
        by the `errors` key
        """

        dict_data = {'detail': ErrorDetail(
            string='Your token has expired, please log in again.',
            code='authentication_failed')}

        rendered_data = json.loads(self.property_renderer.render(dict_data))

        expected_data = {
            'detail': 'Your token has expired, please log in again.'}
        self.assertEqual(rendered_data, expected_data)

    def test_that_data_of_list_types_are_rendered_as_expected(self):
        dummy_data = self.property_data
        dummy_data['address'] = self.property2.address
        dummy_data['coordinates'] = self.property2.coordinates
        serializer = PropertySerializer(
            data=dummy_data)
        serializer.is_valid()
        data = serializer.data
        data['id'] = self.property2.pk
        # The renderer expects serialized data that is an ordered dictionary
        ordered = OrderedDict(data)
        list_data = [ordered]
        payload = OrderedDict({'results': list_data})
        rendered_data = self.property_renderer.render(payload)
        self.assertIn("properties", rendered_data)
        # choices are properly rendered as human-readable values
        self.assertIn("Installments", rendered_data)


class TestPropertyEnquiryRender(BaseTest):
    """all the unittest for PropertyJSONRenderer """

    def test_that_enquiry_data_is_rendered_correctly(self):
        """test that account details are rendered correctly"""

        enquiry_data = {"message": "hello there"}
        rendered_data = self.enquiry_renderer.render(enquiry_data)

        expected_data = '{"data": {"enquiry": {"message": "hello there"}}}'
        self.assertEqual(rendered_data, expected_data)

    def test_data_as_list_is_rendered_correctly(self):
        """test that data in  a list is rendered correctly"""
        data_in_list_format = ["this", "might", "get", "a", "list"]
        rendered_data = self.enquiry_renderer.render(data_in_list_format)

        expected_data = '{"data": {"enquiry": ["this", "might", "get", "a", "list"]}}'
        self.assertEqual(rendered_data, expected_data)

    def test_that_an_error_is_rendered_correctly(self):
        """
        if an error is raised, i.e using serializers.ValidationError, then
        it should be in a format to show this is an error
        """
        Error_detail = {'message': [
            {"ErrorDetail": [{
                "phone": "this field is required"}
            ]}]}
        rendered_data = self.enquiry_renderer.render(Error_detail)

        expected_data = '{"errors": {"message": [{"ErrorDetail": [{"phone": "this field is required"}]}]}}'
        self.assertEqual(rendered_data, expected_data)

    def test_that_errors_are_rendered_as_expected(self):
        dict_data = {"errors": "This error should be properly rendered"
                     }
        rendered_data = self.enquiry_renderer.render(dict_data)

        expected_data = b'{"errors":"This error should be properly rendered"}'
        self.assertEqual(rendered_data, expected_data)

    def test_non_dictionary_is_rendered_correctly(self):
        data = "Not dictionary"
        renderer = PropertyJSONRenderer()
        rendered_data = renderer.render(data=data)
        expected_data = '{"data": {"property": "Not dictionary"}}'
        self.assertEqual(rendered_data, expected_data)
