$script("http://cdnjs.cloudflare.com/ajax/libs/prototype/1.7.0.0/prototype.js","ptype");
$script.ready(
    "ptype",
    function(){

	var api,remote,nearestAttribute,forumLinkClicked,history;
	api = window.fsbbs = {};	

	api.history = history = function(){
	    
	    var h  = window.history || compat(),r = {};
	    
	    var push = (window.history.pushState ? window.history.pushState.bind(window.history) : function(){});

	    var HistoryState = Class.create();
	    HistoryState.prototype = {
		initialize: function(o){
		    this.wrapped = o;
		    // get for how long this resource has been stored
		    this.stored = new Date();
		},
		enter: function(){
		    if(this.wrapped.onHistoryEnter)
		    {
			// call it and give it a chance to refresh
			this.wrapped.onHistoryEnter(this.stored);
		    }
		}
	    };
	    
	    r.pushThing = function(thing){
		var url = "/t/"+thing.id+".html",
		state = new HistoryState(thing),
		title  = thing.title || thing.name || thing.type || "thing";
		push(state,title,url);
	    };
	    
	    return r;
	}();

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

	var humanise = {};
	/* adapted from https://gist.github.com/colmjude  */
	humanise.date = (function() {
	    var measures = {
		second: 1,
		minute: 60,
		hour: 3600,
		day: 86400,
		week: 604800,
		month: 2592000,
		year: 31536000
	    }, chkMultiple = function(amount, type) {
		return (amount > 1) ? amount + " " + type + "s":"a " + type;
	    };

	    return function(thedate) {
		var dateStr, amount, denomination,
		current = new Date().getTime(),
		diff = (current - thedate.getTime()) / 1000; // work with seconds

		if(diff > measures.year) {
		    return  thedate.toLocaleString();
		} else if(diff > measures.month) {
			denomination = "month";
		} else if(diff > measures.week) {
			denomination = "week";
		} else if(diff > measures.day) {
			denomination = "day";
		} else if(diff > measures.hour) {
			denomination = "hour";
		} else if(diff > measures.minute) {
			denomination = "minute";
		} else {
			dateStr = "a few seconds ago";
			return dateStr;
		}
		amount = Math.round(diff/measures[denomination]);
		dateStr = chkMultiple(amount, denomination) + " ago";
		return dateStr;
	    };

	})();

	 
	
	

	templates = {
	    category_topic: new Template('<article data-id="#{id}"><a href="/t/#{id}.html"><h3>#{title}</h3></a>'+
					 'Topic created by <a href="/u/#{original_post.poster_uid}">'+
					 '#{original_post.poster_name}</a>&nbsp;'+
					 '<time timedate="#{original_post.pubdate}">'+
					 '#{original_post.pubdate_human}</time>'+
					 '<div class="clearfix"></div></article>'),
	    thing_start: new Template('<article class="thing thing-#{type}" data-id="#{id}"><header>'+
					'<a rel="self"><h2>#{title}</h2></a>'+
					'</header>'),
	    topic_start: new Template('Topic created by <a data-id="#{op.poster_uid}" '+
				      'href="/u/#{op.poster_uid}"></a>'+
				      '<time datetime="#{op.pubdate}">#{op.pubdate_human}</time>'
				      ),
	    thing_end: new Template("</article>")
	};

	isoToDate = function(d){
	    return new Date(Date.parse(d));
	};

	thingPubdate = function(thing){
	    if (thing.original_post && thing.original_post.pubdate)
	    {
		thing.original_post.pubdate = new Date(Date.parse(thing.original_post.pubdate));
		thing.original_post.pubdate_human = humanise.date(thing.original_post.pubdate);
		
	    }
	    return thing;
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
	    if(thing.type == "category")
	    {
		rendered_contents = [templates.thing_start.evaluate(thingPubdate(thing))];
		rendered_contents = rendered_contents.concat(thing.contents.map(function(sub){
		    return templates.category_topic.evaluate(thingPubdate(sub));
		}));
		rendered_contents.push(templates.thing_end.evaluate(thing));

		$('things').update(rendered_contents.join(""));
		history.pushThing(thing);
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