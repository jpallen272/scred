"""
scred/project.py

Uses REDCap interface and data types defined in other modules to create more complex
classes. Can't go in `dtypes` module because it relies on the `webapi` module, which
lives "above" `dtypes` in the hierarchy.
"""

from . import webapi
from . import dtypes
from .config import DEFAULT_SETTINGS, RedcapConfig

# ---------------------------------------------------
# To construct requester based on class of `requester` arg in RedcapProject.
# All of this might belong in webapi.py though...

def _requester_from_config(cfg):
    return webapi.RedcapRequester(cfg)


def _requester_from_token(token):
    # If given just a token, use default settings and build up a requester
    if len(token) != 32:
        raise ValueError(f"REDCap tokens should be 32 characters long. Got {len(token)}")
    cfg = DEFAULT_SETTINGS
    cfg.update({"token": token})
    return webapi.RedcapRequester(RedcapConfig(cfg))


def _requester_reflexive(requester):
    # If already given a requester, just bounce back
    return requester


def _get_requester_dispatcher():
    # Avoids polluting global namespace. Maps arg's class to function that takes it 
    return {
        RedcapConfig: _requester_from_config,
        str: _requester_from_token,
        webapi.RedcapRequester: _requester_reflexive,
    }


def _create_requester(construct_arg):
    argclass = construct_arg.__class__
    dispatcher = _get_requester_dispatcher()
    try:
        constructor = dispatcher[argclass]
    except KeyError:
        raise TypeError(
            "Project must be built from token (str), config, or None, not "
            f"{construct_arg}"
        ) 
    return constructor(construct_arg)

# ---------------------------------------------------
   
class RedcapProject:
    """
    Main class for top-level interaction.
    """
    def __init__(self, token = None, url = None, *args, **kwargs):
        self.set_url(url)
        self._metadata = None
        if token:
            self.use_token(token)


    @property
    def metadata(self):
        """
        Property that holds the metadata (Data Dictionary) for this project instance.
        """
        # TODO: Implement
        return self._metadata
    
    @metadata.setter
    def metadata(self, value):
        if value is not None:
            raise NotImplementedError
        # TODO: Implement
        self._metadata = value


    def use_token(self, token):
        if not self.url:
            raise AttributeError("You must point to a REDCap instance before using the token")
        self.requester = _requester_from_token(token)
        self.requester.url = self.url


    def set_url(self, url):
        self.url = url


    def post(self, **kwargs):
        return self.requester.post(**kwargs)


    def get_export_fieldnames(self, fields = None):
        """ (From REDCap documentation)
        This method returns a list of the export/import-specific version of field names for all fields
        (or for one field, if desired) in a project. This is mostly used for checkbox fields because
        during data exports and data imports, checkbox fields have a different variable name used than
        the exact one defined for them in the Online Designer and Data Dictionary, in which *each checkbox
        option* gets represented as its own export field name in the following format: field_name +
        triple underscore + converted coded value for the choice. For non-checkbox fields, the export
        field name will be exactly the same as the original field name. Note: The following field types
        will be automatically removed from the list returned by this method since they cannot be utilized
        during the data import process: 'calc', 'file', and 'descriptive'.

        The list that is returned will contain the three following attributes for each field/choice:
        'original_field_name', 'choice_value', and 'export_field_name'. The choice_value attribute
        represents the raw coded value for a checkbox choice. For non-checkbox fields, the choice_value
        attribute will always be blank/empty. The export_field_name attribute represents the export/import-
        specific version of that field name.
        """
        payload_kwargs = {"content": "exportFieldNames"}
        if fields:
            payload_kwargs.update(field=",".join(fields))
        return self.post(payload_kwargs)
    
    def get_records(self, records = None, fields = None, **kwargs):
        payload = {"content": "record"}
        if records:
            payload.update({"records": ",".join(records)})
        if fields:
            payload.update({"fields": ",".join(fields)})
        return self.post(**payload, **kwargs).json()

