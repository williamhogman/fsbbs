$script "http://cdnjs.cloudflare.com/ajax/libs/prototype/1.7.0.0/prototype.js","ptype"
$script "/s/templates.js", "templates"

@$vendor = (ns,lib) ->
        $script "/j/vendor/"+ns+"/"+lib+".js", lib;

$script.ready ["templates","ptype"], ->
        console.log "loading fsbbs"

        api = window.fsbbs = {}

        api.history = history = (->
                r = {}
                window.onpopstate = (ev) ->
                        if(event.state != null)
                                if event.state.handle == "thing"
                                        renderThing(event.state.wrapped)
                                else if event.state.handle == "first"
                                        loadThing(event.state.wrapped)

                e = -> undefined
                if window.history?
                        push = window.history.pushState.bind(window.history)
                        replace = window.history.replaceState.bind(window.history)
                else
                        push = e
                        replace = e

                class HistoryState
                        constructor: (o) ->
                                @wrapped = o
                                @stored = new Date()
                        enter: ->
                                if @wrapped.onHistoryEnter?
                                    @wrapped.onHistoryEnter(this.stored)
                class ThingHistoryState extends HistoryState
                        constructor: (o) ->
                                super o
                                @handle = "thing"
                        enter: -> renderThing(@wrapped)

                class FirstHistoryState extends HistoryState
                        constructor: (o) ->
                                super o
                                @handle = "first"
                r.pushThing = (thing) ->
                        url = "/t/"+thing.id+".html"
                        state = new ThingHistoryState(thing)
                        title = thing.title || thing.name || thing.type || "thing"
                        push(state,title,url)

                (->
                        art = $$("#things article")
                        if art.length > 0
                                firstId =art[0].readAttribute("data-id")
                        else
                                firstId = 1
                        replace new FirstHistoryState(firstId),"","#"
                )()

                return r
                )()
        api.remote = remote = (->
                calls = $H(
                        get_thing:
                                url: "/api/get_thing.json"
                                method: "GET"
                        logout:
                                url: "/api/logout.json"
                                method: "POST"
                        login:
                                url: "/api/login.json"
                                method: "POST"
                        register:
                                url: "/api/register.json"
                                method: "POST"
                );
                fns = $H();
                $H(calls).each (p)->
                        name = p[0]
                        def = $H(p[1])
                        fns[name] = (opt) ->
                                o = def.merge(opt)
                                new Ajax.Request(o.get("url"),o.toObject())
                return fns
                )()

        api.validation = validation = (->
                r = {}
                addError = (elem) ->
                        elem.up().addClassName "error"

                removeError = (elem) ->
                        elem.up().removeClassName "error"

                validation_fns = {
                        notempty: (elem) ->
                                if elem.getValue().trim() == ""
                                        addError(elem)
                                        return false
                                removeError(elem)
                                return true
                }
                class Form
                        constructor: (form,options) ->
                                @form = form
                                @options = $H(options)
                        hook_submit: (fn)-> @form.observe "submit", fn
                        hook_valid: (fn) ->
                                @form.observe "submit", (ev) =>
                                        ev.preventDefault()
                                        if @validate() then fn(this)

                        get: (name) -> @form[name].getValue()

                        validate: ->
                                form = @form
                                @options.all (o) ->
                                        field = form[o[0]]
                                        validators = o[1]
                                        validators.all (o) ->
                                                if Object.isString(o) and validation_fns[o]?
                                                        return validation_fns[o](field)
                                                else if o.isFunction()
                                                        return o(field)
                                                else
                                                        throw "validator must be string or function"


                r.Form = Form;

                class TemplateForm extends Form
                        constructor: (templ,options) ->
                                body = templates[templ].evaluate()
                                title = templates[templ+"_title"].evaluate()
                                form = new Element("form")
                                form.insert(title+body)

                                super(form,options)
                r.TemplateForm = TemplateForm
                return r
        )()

        Button = (name,fn,opt) ->
                o = $H({"href": "#"}).merge(opt).toObject()
                e = new Element("a",o)
                e.update(name)
                e.observe("click",fn)
                return e

        api.modal = modal = (->
                r = {}
                modals = []

                class ModalWindow
                        constructor: (id) ->
                                @element = new Element("div",class: "modalWindow", id: id)
                        show: ->
                                # this works because the setCallbacks
                                # (and therefore.defer) are queued up
                                # after oneanother.
                                @element.addClassName.bind(this.element).defer("show")
                                if cb? then cb.defer()

                        insert: (elem) -> @element.insert(elem)
                        hideAndDelete: ->
                                @element.removeClassName("show")
                                (=> @element.remove()).delay(1)
                        addIntoDOM: ->
                                $(document.body).insert(@element)


                r.ModalWindow = ModalWindow
                return r
        )()

        api.auth = auth = (->
                loggedin = false
                uid = null
                username = null

                r = {}
                r.setUser = (userid,uname) ->
                        if not userid? then return
                        else if userid < 1 then return console.warn "tried to set user to invalid ID"
                        username = uname
                        uid = userid
                        loggedin = true
                        r.ui.update()


                r.doLogout = (cb) ->
                        remote.logout onSuccess: ->
                                loggedIn = false
                                uid = null
                                if cb? then cb()
                                r.ui.update()
                r.isLoggedIn = -> loggedin

                r.ui = (->
                        e = {}
                        loginbar = $$(".loginbar")[0]

                        modalForm = (name,opt,fn) -> ->
                                frm = new validation.TemplateForm(name,opt)
                                modal = new modal.ModalWindow(name)
                                modal.insert(frm.form)
                                modal.addIntoDOM()
                                modal.show()
                                frm.hook_valid(->
                                        fn(frm)
                                        modal.hideAndDelete()
                                        )

                        showLoginModal = modalForm "modal_login",
                                {username: ["notempty"],password: ["notempty"]}, (form) ->
                                        un = form.get("username")
                                        pw = form.get("password")
                                        remote.login(
                                                parameters:
                                                        username: un
                                                        password: pw
                                                onSuccess: (resp) ->
                                                        res = resp.responseJSON
                                                        if res.status == "success"
                                                                r.setUser(res.uid,un)
                                                        else if res.status == "invalid"
                                                                r.setUser(res.uid)
                                                        else
                                                                form.setError("password","Incorrect username or password")
                                                onFailure: (resp) -> form.setError(null,"Something went wrong")
                                        )






                        showRegisterModal = modalForm "modal_register",
                                {username: ["notempty"], password: ["notempty"]},(form) ->
                                        un = form.get("username")
                                        pw = form.get("password")
                                        remote.register(
                                                parameters:
                                                        username: un
                                                        password: pw
                                                onSuccess: (resp) ->
                                                        res = resp.responseJSON
                                                        if res.status == "success"
                                                                r.setUser(res.uid,un)
                                                        else if res.status == "invalid"
                                                                r.setUser(res.uid)
                                                        else
                                                                form.setError("username","Username taken")
                                                onFailure: -> form.setError(null,"Something went wrong")
                                        )

                        e.update = ->
                                if loggedin
                                        msg = templates.status_user.evaluate(username: username)
                                        btn_logout = Button("Logout",(-> r.doLogout()),class: "button logout-btn")
                                        loginbar.update(msg).insert(btn_logout)
                                else
                                        msg = templates.status_guest.evaluate()
                                        btn_login = Button("Login",showLoginModal,class: "button login-btn")
                                        btn_reg = Button("Register",showRegisterModal,class: "button regoster-btn")
                                        loginbar.update(msg).insert(btn_login).insert(btn_reg)
                        return e
                )()
                r.setUser(window.initial_uid)
                return r
        )()


        humanise = {}
        humanise.date = (->
                measures = {
                        second: 1,
                        minute: 60,
                        hour: 3600,
                        day: 86400,
                        week: 604800,
                        month: 2592000,
                        year: 31536000
                }

                chkMultiple = (amount,type) ->
                        if amount > 1
                                return amount+" "+type+"s"
                        return "a "+type

                return (thedate) ->
                        current = new Date().getTime()
                        diff = current - thedate.getTime() /1000

                        if diff > measures.year then return thedate.toLocaleString()
                        else if diff > measures.month then denom = "month"
                        else if diff > measures.week then denom = "week"
                        else if diff > measures.day then denom = "day"
                        else if diff > measures.hour then denom = "hour"
                        else if diff > measures.minute then denom = "minute"
                        else return "a few seconds ago"

                        amount = Math.round diff/measures[denom]
                        return chkMultuple(amount,denom) + " ago"

                )()

        parseThing = (thing) ->
                # crates extra properties on a downloaded thing
                # and performs conversions to markdown

                if thing.original_post? and thing.original_post.pubdate?
                        op = thing.original_post
                        op.pubdate = new Date(Date.parse(op.pubdate))
                        op.pubdate_human = humanise.date op.pubdate
                if thing.pubdate?
                        thing.pubdate = new Date(Date.parse(thing.pubdate))
                        thing.pubdate_human = humanise.date thing.pubdate

                if thing.text then thing.text = md.toHTML(thing.text)

                return thing

        # walks the DOM untill it finds an attribute with the passed in name
        nearestAttribute = (elem,attr) ->
                res = null
                while res == null
                        res = elem.readAttribute(attr)
                        up = elem.up()
                        if up == elem
                                return null
                        elem = up
                return res

        updateInteractions = (thing) ->
                # Updates the interactions (posting etc) ui
                # according to the current login state and
                # page (being a category or a topic)
                elem = $("interations")
                if not auth.isLoggedIn()
                        elem.update "<p>You need to login in order to post</p>"
                        return

                if thing.type == "category"
                        frm = templates.form_new_topic.evaluate(thing)
                        elem.update(frm)
                        md.addEditor("-newtopic")
                else if thing.type == "topic"
                        frm = templates.form_new_post.evaluate(thing)
                        elem.update(frm)
                        md.addEditor("-newpost")
                else elem.update("")

        loadThing = (tid) ->
                # loads a thing from the server
                remote.get_thing(
                        parameters:
                                id: tid
                        onSuccess: -> renderThing(response.responseJSON.thing)
                )
        renderThing = (thing) ->
                # renders the passed in thing
                rendered = [templates.thing_start.evaluate(parseThing(thing))]
                if thing.type == "category"
                        rendered = rendered.concat(thing.contents.map( (sub) ->
                        templates.category_topic.evaluate(parseThing(sub))
                        ))
                else if thing.type == "topic"
                        rendered.push templates.topic_op.evaluate(parseThing(thing.original_post))
                        rendered.concat thing.contents.map (sub)->
                                templates.topic.evaluate(parseThing(sub))

                rendered.push templates.thing_end.evaluate thing
                $("things").update rendered_contents.join ""
                history.pushThing(thing)
                addLinkEvents()
                updateInterations()

        forumLinkCliked = (ev) ->
                id = nearestAttribute(this,"data-id")
                if id?
                        ev.stop()
                        loadThing(id)
        addLinkEvents = ->
                $$("article[data-id] a").each (item) ->
                        item.observe "click", forumLinkClicked
        addLinkEvents()

        md = {}
        $script.ready "markdown", ->
                converter = Markdown.getSanitizingConverter()
                md.addEditor = (postfix) ->
                        if not $("wmd-input-"+postfix)?
                                console.warn(postfix,"missing")
                                return false
                        editor = new Markdown.Editor(converter,postfix)
                        editor.run()
                        return true

                md.toHTML = (text) -> converter.makeHtml(text)

                md.addEditor("-newtopic")
                md.addEditor("-newpost")

        setTimeout(auth.ui.update,3)
        return undefined;






















