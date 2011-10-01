$script("http://cdnjs.cloudflare.com/ajax/libs/prototype/1.7.0.0/prototype.js","ptype");
$script.ready(
    "ptype",
    function(){
	var api,remote,nearestAttribute,forumLinkClicked;
	api = window.fsbbs = {};	

	api.remote = remote = function(){
	    var calls = 
		{
		    "get_thing": {url: "/api/get_thing.json", method: "GET"}
		};
	    var fns = $H();
	    $H(calls).each(function(p){
		// get our name and defaults
		var name= p[0],def = $H(p[1]);
		fns[name] = function(opt) {
		    // merge our args with the 
		    var o = def.merge(opt);
		    return new Ajax.Request(o.get('url'),o.toObject());
		};
	    });
	    return fns;
	}();
	 
	
	

	templates = {
	    category_topic: new Template('<article data-id="#{id}"><a href="/t/#{id}.html"><h3>#{title}</h3></a>'+
					 'Topic created by <a href="/u/#{original_post.poster_uid}">'+
					 '#{original_post.poster_name}</a>&nbsp;'+
					 '<time timedate="#{original_post.pubdate}">'+
					 '#{original_post.pubdate}</time>'+
					 '<div class="clearfix"></div></article>'),
	    thing_start: new Template('<article class="thing thing-#{type}" data-id="#{id}"><header>'+
					'<a rel="self"><h2>#{title}</h2></a>'+
					'</header>'),
	    topic_start: new Template('Topic created by <a data-id="#{op.poster_uid}" '+
				      'href="/u/#{op.poster_uid}"></a>'+
				      '<time datetime="#{op.pubdate}">#{op.pubdate_nice}</time>'
				      ),
	    thing_end: new Template("</article>")
	};


	/** walks the DOM untill it finds an attribute with the passed in name */
	nearestAttribute = function(elem,attr){
	    var res;
	    while(res == null) /* works b/c undefined == null && undefined !== null */
	    {
		res = elem.readAttribute(attr);
		up = elem.up();
		if(up == elem)
		    return null;
		elem = up;
	    }
	    return res;
	};
	
	loadThing = function(tid){
	    var success = function(response){
		renderThing(response.responseJSON.thing);
	    };
	    remote.get_thing({"parameters": {"id": tid}, onSuccess: success});
	};
	
	renderThing = function(thing){
	    console.log(thing.type);
	    if(thing.type == "category")
	    {
		rendered_contents = [templates.thing_start.evaluate(thing)];
		rendered_contents = rendered_contents.concat(thing.contents.map(function(sub){
		    return templates.category_topic.evaluate(sub);
		}));
		rendered_contents.push(templates.thing_end.evaluate(thing));

		$('container').update(rendered_contents.join(""));
		
	    }
	};

	forumLinkClicked = function(ev){
	    var id =  nearestAttribute(this,"data-id");
	    if(id != null)
	    {
		ev.stop();
		loadThing(id)

	    }
	};
	
	$$("article[data-id] a").each(function(item){
	    item.observe("click",forumLinkClicked);
	});
	
    });