$script("http://cdnjs.cloudflare.com/ajax/libs/prototype/1.7.0.0/prototype.js","ptype");
$script.ready("ptype",
	      function(){
		  api = window.fsbbs = {};

		  forumLinkClicked = function(){
		      var cur = this;
		      var id = cur.readAttribute("data-id")
		      while(id === null)
			  {
			      cur = cur.up();
			      id = cur.readAttribute("data-id");
			  }
		      alert(id);
		      return true;
		  };
		  
		  $$("article[data-id] a").each(function(item){
						    item.observe("click",forumLinkClicked);
						});
		  
	      });