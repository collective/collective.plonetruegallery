(function($){
    $.fn.imagesLoaded = function(callback){
      var elems = this.filter('img'),
          len   = elems.length;

      elems.bind('load',function(){
          if (--len <= 0){ callback.call(elems,this); }
      }).each(function(){
         // cached images don't fire load sometimes, so we reset src.
         if (this.complete || this.complete === undefined){
            var src = this.src;
            // webkit hack from http://groups.google.com/group/jquery-dev/browse_thread/thread/eee6ab7b2da50e1f
            this.src = '#';
            this.src = src;
         }  
      }); 
    };
    
    function set_controls_position(container){
        var width = container.find('img').width();
        var left = (width/2) - 43;
        container.find('div.gallery-portlet-controls').css("left", left);
    }
    
    function get_image(link){
        var linkele = link[0];
        if(linkele.active != undefined && linkele.active){
            return;
        }
        linkele.active = true;
        var container = link.parents('dl.applied-portlet-gallery');
        var controls = link.parents('div.gallery-portlet-controls');
        var portlet_item = link.parents('dd.portletItem');
        var next = controls.find('span.next a');
        var prev = controls.find('span.prev a');        
        var img = container.find('img');
        
        $.ajax({
            url : '@@get-image-for-gallery-portlet',
            data : link.attr('href').split('?')[1],
            type : 'GET',
            success : function(data, results){
                eval("var json="+data);
                //create new image now so it'll be done loading faster...
                var newimg = document.createElement('img');
                newimg.src = json.src;
                newimg.width = img.width();
                if(img.attr('height') !== undefined){
                    newimg.height = img.height();
                }
                newimg = $(newimg);
                newimg.css('display', 'none');
                portlet_item.css('height', img.height());
                
                img.fadeOut(1000, function(){
                    img.replaceWith(newimg);
                    
                    newimg.imagesLoaded(function(){
                        portlet_item.animate({ height : $(this).height() }, 500, 'linear');
                        $(this).fadeIn(1000, function(){
                            linkele.active = false;
                        });
                    }, newimg)
                    
                    var linked = newimg.parent()
                    linked.attr('href', json['image-link']);
                    linked.attr('title', json['title']);
                    linked.attr('alt', json['description']);
                    
                    next.attr('href', next.attr('href').split('?')[0] + '?' + json['next-url']);
                    prev.attr('href', prev.attr('href').split('?')[0] + '?' + json['prev-url']);
                    set_controls_position(container);
                });
            }
        });
    }
    
    function get_timeout_ele(portlet){
        if(portlet.hasClass('portletItem')){
            portlet = portlet.parent();
        }
        return portlet.find("input.timeout_id");
    }
    
    function get_timeout_id(portlet){
        var timeout_id = get_timeout_ele(portlet);
        if(timeout_id.size() == 0){
            return 0;
        }else{
            return parseInt(timeout_id.attr('value'));
        }
    }
    
    function set_timeout_id(portlet, val){
        var timeout_id = get_timeout_ele(portlet);
        if(timeout_id.size() == 0){
            portlet.append('<input type="hidden" name="timeout_id" class="timeout_id" value="' + val + '" />');
        }else{
            timeout_id.attr('value', val);
        }
    }
    
    function perform_play(portlet){
        portlet.find('span.next a').trigger('click');
        set_timeout_id(portlet, setTimeout(function(){perform_play(portlet);}, 5000));
    }   
     
    function play(portlet){
        portlet.find('span.play-pause').addClass('timed');
        set_timeout_id(portlet, setTimeout(function(){perform_play(portlet);}, 5000));
    }
    
    function pause(portlet){
        clearTimeout(get_timeout_id(portlet));
        portlet.find('span.play-pause').removeClass('timed');
    }
    
    $(document).ready(function(){
        
        $('dl.portletGallery span.next a,dl.portletGallery span.prev a').click(function(){
            get_image($(this));
            return false;
        });
        
        $('dl.portletGallery span.play-pause').css({'display':'inline'});
        
        var portlets = $('dl.portletGallery');
        portlets.addClass('applied-portlet-gallery');
        
        portlets.each(function(){
            var portlet = $(this);
            set_controls_position(portlet);
            if(portlet.hasClass('timed')){
                play(portlet);
            }else{
                pause(portlet);
            }
        });
        
        $('dl.portletGallery span.play-pause a').click(function(){
            var portlet = $(this).parent().parent().parent();
            if(portlet.find('span.play-pause').hasClass('timed')){
                pause(portlet);
            }else{
                play(portlet);
            }
            return false;
        });
        
        $('dl.portletGallery').hover(
            function(){
                var controls = $(this).find('div.gallery-portlet-controls:not(.hide)');
                controls.fadeIn();
            },
            function(){
                var controls = $(this).find('div.gallery-portlet-controls:not(.hide)');
                controls.fadeOut();
            }
        );
    });
})(jQuery);