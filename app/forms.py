import copy
from collections import OrderedDict


# https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5/Constraint_validation
# form_name (str): The name which will be applied to the form in which this field is placed
# label (str): The label which will be applied to the field. Ex: Number of Sensors
# html5_constrant: See https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5/Constraint_validation
# valid_feedback (str): The message to display when the user types something which
#                       meets the above defined validation constraint
# invalid_feedback (str): The message tobe displayed when the constraint is not met
# default_value (str): The default value that you would like to occupy the field
# required (bool): Whether the field is or is not required
# description (str): The description which you would like to appear in the help page
# placeholder (str): The placeholder text which will appear inside of the field
# input_type: See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input
class Field:
    def __init__(self, form_name, label, html5_constraint=None, valid_feedback='Good to go!',
                 invalid_feedback='This is not a valid value.', disabled=False, hidden=False, default_value=None,
                 required=False, description=None, placeholder=None, input_type='text'):
        self.form_name = 'form_' + form_name
        self.field_id = form_name + '_field'
        self.label = label
        self.description = description
        self.placeholder = placeholder
        self.input_type = input_type
        self.html5_constraint = html5_constraint
        self.valid_feedback = valid_feedback
        self.invalid_feedback = invalid_feedback
        self.default_value = default_value
        self.disabled = disabled
        self.hidden = hidden

        # This is the HTML file generally associated with displaying this field.
        # You don't have to use this, but it is handy for displaying things in a loop.
        self.include_html = "text_input.html"

        if required:
            self.required = 'required'

    # This is a mammoth hack because Jinja2 doesn't allow assignment within
    # templates. To get around this, I provide this method which simply modifies
    # various fields within the object and then returns the copy of the object.
    # This allows the code to effectively modify the object - without modifying
    # the object.

    # This function is meant for use when you have something like a for loop
    # in Jinja and you need to provide different variables to a button on each
    # iteration of the loop.
    # form_name (str): The updated form name you would like returned with the copy
    #                  of your object.
    # field_id (str): The updated field id you would like returned.
    # args: See: https://stackoverflow.com/questions/3394835/args-and-kwargs
    #       for a good explanation of args. This is for providing arbitrary arguments
    #       to your reaction file. For example, you could provide a new argument
    #       called 'server_1'. Within the reaction file, you could access this
    #       by calling object.args[0]
    def change_values(self, form_name, field_id, *args):
        copy_of_self = copy.deepcopy(self)
        copy_of_self.form_name = form_name
        copy_of_self.field_id = field_id
        copy_of_self.args = args
        return copy_of_self


# button_text (str): The text you want displayed on the button itself
# reaction_file (str): A file containing the javascript you would like executed
#                      when someone clicks the button. This will be included as
#                      part of the else condition.
# For all other arguments see field. This class inherits from field so any argument
# which may be applied to field may also be applied here.
class Button(Field, object):
    def __init__(self, button_text, reaction_file=None, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.button_id = kwargs.get('form_name') + '_button'
        self.button_text = button_text
        self.reaction_file = reaction_file

        # This is the HTML file generally associated with displaying this field.
        # You don't have to use this, but it is handy for displaying things in a loop.
        self.include_html = "button.html"

    # This is a mammoth hack because Jinja2 doesn't allow assignment within
    # templates. To get around this, I provide this method which simply modifies
    # various fields within the object and then returns the copy of the object.
    # This allows the code to effectively modify the object - without modifying
    # the object.

    # This function is meant for use when you have something like a for loop
    # in Jinja and you need to provide different variables to a button on each
    # iteration of the loop.
    # form_name (str): The updated form name you would like returned with the copy
    #                  of your object.
    # field_id (str): The updated field id you would like returned.
    # button_id (strp): The updated button id you would like returned.
    # args: See: https://stackoverflow.com/questions/3394835/args-and-kwargs
    #       for a good explanation of args. This is for providing arbitrary arguments
    #       to your reaction file. For example, you could provide a new argument
    #       called 'server_1'. Within the reaction file, you could access this
    #       by calling object.args[0]
    def change_values(self, form_name, field_id, button_id, *args):
        copy_of_self = copy.deepcopy(self)
        copy_of_self.form_name = form_name
        copy_of_self.field_id = field_id
        copy_of_self.button_id = button_id
        copy_of_self.args = args
        return copy_of_self


class GenericButton:
    def __init__(self, form_name, label, description=None, callback=None):
        self.form_name = form_name
        self.generic_button_id = form_name + '_generic_button'
        self.css_class = form_name + '_generic_button_class'
        self.label = label
        self.description = description
        self.callback = callback


class CheckBox:
    def __init__(self, form_name, label, disabled=False, description=None):
        self.form_name = form_name
        self.checkbox_id = form_name + '_checkbox'
        self.field_id = form_name + '_checkbox'  # This is for niche cases where we
        # a foor loop to loop over fields
        # and checkboxes
        self.css_class = form_name + '_checkbox_class'
        self.label = label
        self.description = description
        self.disabled = disabled


class DropDown:
    def __init__(self, form_name, label, options, dropdown_text, callback=None, description=None, default_option=None):
        self.form_name = 'form_' + form_name
        self.dropdown_id = form_name + '_dropdown'
        self.label = label
        self.description = description
        self.options = options
        self.dropdown_text = dropdown_text
        self.default_option = default_option
        self.callback = callback

        # This is the HTML file generally associated with displaying this field.
        # You don't have to use this, but it is handy for displaying things in a loop.
        self.include_html = "dropdown.html"

    def change_values(self, form_name, dropdown_id, *args):
        copy_of_self = copy.deepcopy(self)
        copy_of_self.form_name = form_name
        copy_of_self.dropdown_id = dropdown_id
        copy_of_self.args = args
        return copy_of_self


# name (str): The name of your modal (no spaces)
# modal_title (str): The title that will appear along with the modal box
# modal_text (str): The text that will appear in the modal box
# secondary_button_text (str): The label of the secondary button in the modal
# primary_button_text (str): The text on the primary button

# The below explain the additional variables that you might have need to reference
# but are not necessary for calling the modal
# button_id (str): The id of the button that will trigger this modal popup. You must
#                  must provide this yourself. You could use GenericButton.
# modal_id (str): The ID of the modal box itself
# modal_label_id (str): The ID of the modal label itself
# button_id_secondary (str): The ID of the secondary button
# button_id_primary (str): The Id of the primary button
# secondary_button_close: True if you want the secondary button to close the modal
#                         and false if you don't
class ModalPopUp:
    def __init__(self, name, modal_title, modal_text, primary_button_text=None, secondary_button_text=None,
                 secondary_button_close=True):
        self.name = name
        self.button_id = name + "_button_id"
        self.modal_id = name + "_modal_id"
        self.modal_label_id = name + "_modal_label_id"
        self.modal_title = modal_title
        self.modal_text = modal_text
        self.button_id_secondary = name + "_modal_button_id_secondary"
        self.secondary_button_text = secondary_button_text
        self.button_id_primary = name + "_modal_button_id_primary"
        self.primary_button_text = primary_button_text
        self.secondary_button_close = secondary_button_close

    def change_values(self, i):
        copy_of_self = copy.deepcopy(self)
        copy_of_self.button_id = self.name + "_button_id_" + str(i)
        copy_of_self.modal_id = self.name + "_modal_id_" + str(i)
        copy_of_self.modal_label_id = self.name + "_modal_label_id_" + str(i)
        copy_of_self.button_id_secondary = self.name + "_modal_button_id_secondary_" + str(i)
        copy_of_self.button_id_primary = self.name + "_modal_button_id_primary_" + str(i)
        return copy_of_self


class ErrorForm:
    def __init__(self, text):
        self.error_text = text


class CharacterForm:
    # See https://www.tutorialspoint.com/javascript/javascript_regexp_object.htm

    # This version of the regex will only let you set an IP address up to the end of
    # the class C address space (223.255.255.0). It will also prevent you from selecting
    # a final octet of 255 (which in our scenario will not be a valid IP)
    ip_constraint = 'pattern=^((2[0-2][0-3])|(1\d\d)|([1-9]?\d))(\.((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]?\d))){2}\.((25[0-4])|(2[0-4]\d)|(1\d\d)|([1-9]?\d))$'

    # This version of the regex allows you to enter IP addresses or subnets
    ip_constraint_with_subnet = 'pattern=((^|\.)((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]?\d))){4}$'
    # See: https://stackoverflow.com/questions/34758562/regular-expression-how-can-i-match-all-numbers-less-than-or-equal-to-twenty-fo
    # ^ I left the line above because it was helpful, but I didn't end up using it
    # in the final version
    # for a good explanation of this type of regex. I got the original code from: https://gist.github.com/nikic/4162505
    cidr_constraint = "pattern=(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(3[0-2]|[1-2]?[0-9])";

    # If you need to add elements to the navbar you can do it here
    navbar_elements = OrderedDict([
        ('Character Lookup', {'url': '/character', 'key': 'tn_character'})
        , ('Help', {'url': '/help', 'key': 'tn_help'})])

    character = Button(
        form_name='character_input'
        , label='Character'
        , button_text='Look Up!'
        , placeholder="Enter Character Here!"
        , input_type='text'
        , required=True
        , valid_feedback='Hit "Look Up!"'
        , reaction_file='button_reaction_lookup_character.js')

    dhcp_settings = [character]