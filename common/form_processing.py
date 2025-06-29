def parse_bulk_delete_form(request, prefix):
    post_data = request.POST.dict()
    post_data.pop('csrfmiddlewaretoken')
    
    # Parses the form data
    id_list = []
    for raw_id in post_data.keys():
        try:
            media_id = int(raw_id.removeprefix(prefix)) 
            id_list.append(media_id)
        except ValueError:
            # Invalid data (like string "prefix_noninteger") just gets ignored
            pass
    
    return id_list