// This will contact the node, run the _node route, and the value provided
// here will be used in the node.html template as the loop count variable
// to determine how many node forms should be made. (IE if the user types
// 5 in Number of nodes it will be transfered as the variable node_count)
// here.

$.get("{{ url_for('_lookup_character') }}", { character_to_lookup: $( 'input[name={{ object.field_id }}]' ).val(), save_character: $('#{{ form.save_character_checkbox.checkbox_id }}').is(":checked") }, function(data){

  // The hide method is here because effects only work if the element
  // begins in a hidden state
  $( "#{{ [object.form_name, 'accordion'] | join('_') }}" ).html(data).hide().slideDown("slow");
  //$( "#{{ [object.form_name, 'accordion'] | join('_') }}" ).html("<p>balls</p>").hide().slideDown("slow");

});
