/**
 * Author:    Sumit Sharma
 * Created:   30.01.2024
 * 
 * (c) Copyright by ClusterVision Solutions B.V.
 * jQuery plugin for Rack Management.
 *
 * Requires jquery-3.6.0.js.
 *
 * This code is part of the TrinityX software suite
 * Copyright (C) 2023  ClusterVision Solutions b.v.
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>
 */

var source_rack, source_slot;
var devices = [];

function each_draggable(slot_num, height, name, rack_name) {
    var device_height = Number(height);
    var device_position = Number(slot_num);
    var till = device_height + device_position;

    for (let index = 0; index < device_height; index++) {
      var slot = Number(device_position+index);
      $("."+slot+"-"+rack_name).addClass("ui-state-highlight");
    }

    $("#"+name).draggable({
      start: function() { 
        source_rack = $(this).parent().attr('rack');
        source_slot = $(this).parent().attr('slot');
        if ($(this).attr("size") > 1){
          $(this).parent().parent().nextAll().add($(this).parent().parent()).slice(0, $(this).attr("size")).find('.rack-slot').removeClass("ui-state-highlight");
        } else {
          $(this).parent().removeClass("ui-state-highlight");
        }
      },
      revert: function() {
        $(this).parent().addClass( "ui-state-highlight" ).find( "p" ).html();
        $(this).parent().nextAll().slice(0, $(this).attr("size")-1).addClass( "ui-state-highlight" ).find( "p" ).html();
        if ($(this).hasClass('drag-revert')) { $(this).removeClass('drag-revert'); return true; } 
    },
    stop: function(event, ui) {
    },
      cursor: "move",
      scroll: true,
      snap: ".snaptarget"
    }); 
  devices.push(name);
  
}


function load_class(devices) {
  for (let i = 0; i < devices.length; i++) {
    $("#"+devices[i]).parent().nextAll().add($("#"+devices[i]).parent()).slice(0, $("#"+devices[i]).attr("size")).addClass("ui-state-highlight");
  }
  
}

function extend_view(id){
  $(id).toggle();
}

function update(name=null, type=null, rack=null, position=null, orientation=null){
  var response;
  var payload = {"name": name, "type": type, "rack": rack, "position": position, "orientation": orientation};
  payload = JSON.stringify(payload);
  $.ajax({
      //url: window.location.href+"/update",
      url: "/update",
      type: 'POST',
      data: JSON.stringify(payload),
      dataType: 'json',
      contentType: 'application/json; charset=UTF-8',
      async: false,
      success: function(response_data) {
          console.log(response_data);
          response = response_data
      }
  });

  console.log(response);
  return response;
}


function back_to_inventory(params) {
    $( "#devices" ).droppable({
      classes: {
        "ui-droppable-active": "ui-state-active",
        "ui-droppable-hover": "ui-state-hover"
      },
      drop: function( event, ui ) {
          if ($(ui.draggable).parent().attr("class").includes("ui-state-highlight")){
            $(ui.draggable).parent().removeClass( "ui-state-highlight" ).find( "p" ).html();
            $(ui.draggable).parent().nextAll().slice(0, $(ui.draggable).attr("size") - 1).removeClass( "ui-state-highlight" ).find( "p" ).html();
          }
          $(ui.draggable).detach().css({top: 0,left: 2}).appendTo(this);
          $(this).addClass( "ui-state-highlight" ).find( "p" ).html();
          $(this).nextAll().slice(0,$(ui.draggable).attr("size")-1).addClass( "ui-state-highlight" ).find( "p" ).html();
          var name = $(ui.draggable).attr('id');
          var type = $(ui.draggable).find("input[name='type']").val();
          var rack = $(this).find("input[name='rack']").val();
          var position = Number($(this).find("input[name='position']").val());
          var result = update(name, type, rack, position);
          $(".toast-body").html();
          $(".toast-body").html(name + " Removed from Rack.");
          $("#rack-remove-toast").toast("show");
      }
    });
}


function revert_back(params) {

  $( ".revert-back" ).droppable({
    drop: function( event, ui ) {
      $(ui.draggable).addClass('drag-revert');
    }
  });
  
}


function drag_drop(params) {
    $(".droppable").droppable({
      // greedy: true,
      // tolerance: true,
      classes: {
        "ui-droppable-active": "ui-state-active",
        "ui-droppable-hover": "ui-state-hover"
      },
      drop: function(event, ui) {
        var exact_div;

       // console.log($(this).parent().nextAll());
       // console.log($(ui.draggable).attr("size"));

        if (Number($(this).parent().nextAll().length) < Number($(ui.draggable).attr("size"))){
          $(ui.draggable).addClass('drag-revert');
        } 
         else {


          if ($(this).attr("class").includes("ui-state-highlight") && (Number($(this).children().length) == 0)){
            console.log("this condition");
      
            exact_div = $(this).parent().prevAll().children().children("div.draggable:first").parent();
            var big_element = Number($(this).parent().prevAll().children().children("div.draggable:first").attr("size"));
            $(ui.draggable).detach().css({top: 0,left: 0}).appendTo(exact_div);
            $(ui.draggable).css('height', big_element*30-2);
            $(ui.draggable).attr("size", big_element);
            
            var total_elements = Number($(this).parent().prevAll().children().children("div.draggable:first").parent().find("div").length);
            var each_width = 220 / total_elements;
            each_width = String(each_width-2)+'px';
            if (total_elements != 1){ $(this).parent().prevAll().children().children("div.draggable:first").parent().find("span").hide(); } else { $(this).parent().prevAll().children().children("div.draggable:first").parent().find("span").show(); }
            $(this).parent().prevAll().children().children("div.draggable:first").parent().find("div").css('width', each_width);
    
           
          }
  
          else {   
  
          if ($(ui.draggable).attr("size") > 1){                ///////// --> If Device height is bigger
  
            if(Number($(this).find("div").attr("size")) > $(ui.draggable).attr("size")){
              var big_element = Number($(this).find("div").attr("size"));
            } else {
              var big_element = Number($(ui.draggable).attr("size"));
            }
            if ($(this).parent().nextAll().add($(this).parent()).slice(0, big_element).find('.rack-slot').hasClass("ui-state-highlight")){
              $(ui.draggable).addClass('drag-revert');
              console.log("not enough space");
            } else {

              $(this).parent().nextAll().add($(this).parent()).slice(0, big_element).find('.rack-slot').addClass("ui-state-highlight");          
              $(ui.draggable).detach().css({top: 0,left: 0}).appendTo(this);
              $(ui.draggable).css('height', big_element*30-2);
              $(ui.draggable).attr("size", big_element);
              $(this).find("div").css('height', big_element*30-2);
              $(this).find("div").attr("size", big_element);
  
            console.log("this another condition");

            }

  
            
  
          } else {                 ///////// --> If Device height is Normal
  
            var total_elements = Number($(this).find("div").length);
            var big_element = Number($(this).find("div").attr("size"));
            
            if (total_elements > 1){                ///////// --> If Slot has Device
  
              $(this).parent().nextAll().add($(this).parent()).slice(1, big_element).find('.rack-slot').addClass("ui-state-highlight");            
              $(ui.draggable).detach().css({top: 0,left: 0}).appendTo(this);
              $(ui.draggable).css('height', big_element*30-2);
              $(ui.draggable).attr("size", big_element);
              //$(this).addClass("ui-state-highlight" );
              //$(ui.draggable).css('height', $("."+source_slot+"-"+source_rack).children("div").attr("size")*30-2);
              console.log("this new condition");
            } else {                ///////// --> If Slot don't have Device
  
              //console.log(big_element);
              //console.log(big_element*30-2);
              //console.log(total_elements);
  
              var source_size = Number($("."+source_slot+"-"+source_rack).children("div").attr("size"));
              //console.log(source_size);
              $(ui.draggable).detach().css({top: 0,left: 0}).appendTo(this);
              $(ui.draggable).attr("size", big_element);
              $(ui.draggable).css('height', big_element*30-2);
              $(this).addClass("ui-state-highlight" );
              
              console.log("this extra condition");
            }
            
          }
          
  
          //$(ui.draggable).detach().css({top: 0,left: 0}).appendTo(this);
          //$(this).addClass("ui-state-highlight" );
         // $(this).parent().nextAll().slice(0, $(ui.draggable).attr("size") -1).addClass("ui-state-highlight");
          var total_elements = Number($(this).find("div").length);
          var each_width = 220 / total_elements;
          each_width = String(each_width-2)+'px';
          if (total_elements != 1){ $(this).find("span").hide(); } else { $(this).find("span").show(); }
          $(this).find("div").css('width', each_width);
  
          
             var source_div_length = Number($("."+source_slot+"-"+source_rack).children("div").length);
            // console.log(source_div_length);
            // console.log($("."+source_slot+"-"+source_rack).children("div").attr("size"));
  
             //$(ui.draggable).css('height', $("."+source_slot+"-"+source_rack).children("div").attr("size")*30-2);
  
  
          if (source_div_length >= 1){
            var each_div_width = 220 / source_div_length;
            each_div_width = String(each_div_width-2)+'px';
            
          if (source_div_length == 1){ $("."+source_slot+"-"+source_rack).children("div").find("span").show(); }
            $("."+source_slot+"-"+source_rack).children("div").css('width', each_div_width);
          }    
     
          }
  
          if ($("."+source_slot+"-"+source_rack).find("div.draggable").length >= 1){
            //$("."+source_slot+"-"+source_rack).parent().nextAll().add($(this).parent()).slice(1, big_element).find('.rack-slot').addClass("ui-state-highlight"); 
            $("."+source_slot+"-"+source_rack).addClass("ui-state-highlight");
            //console.log($("."+source_slot+"-"+source_rack).find("div.draggable"));
            $("."+source_slot+"-"+source_rack).parent().nextAll().add($("."+source_slot+"-"+source_rack).parent()).slice(1, $(ui.draggable).attr("size")).find('.rack-slot').addClass("ui-state-highlight");
          }



        }
        
        //$(ui.draggable).css('zIndex', '0');
        

        

      /*  if ($(this).attr("class").includes("ui-state-highlight") ){
          $(ui.draggable).addClass('drag-revert');
        }
        else if ($(this).nextAll().slice(0, $(ui.draggable).attr("size")-1).hasClass("ui-state-highlight") ){
          $(ui.draggable).addClass('drag-revert');
        }
        else if (Number($(this).parent().nextAll().length) < Number($(ui.draggable).attr("size"))){
          $(ui.draggable).addClass('drag-revert');
        } else {
          if ($(ui.draggable).parent().attr("class").includes("ui-state-highlight")){
            $(ui.draggable).parent().removeClass( "ui-state-highlight" ).find( "p" ).html();
            $(ui.draggable).parent().nextAll().slice(0,$(ui.draggable).attr("size")-1).removeClass( "ui-state-highlight" ).find( "p" ).html();
          } 
          $(ui.draggable).detach().css({top: 0,left: 2}).appendTo(this);
          $(this).addClass( "ui-state-highlight" ).find( "p" ).html();
          $(this).nextAll().slice(0,$(ui.draggable).attr("size")-1).addClass( "ui-state-highlight" ).find( "p" ).html();
          var name = $(ui.draggable).attr('id');
          var type = $(ui.draggable).find("input[name='type']").val();
          var orientation = $(this).find("input[name='orientation']").val();
          var rack = $(this).find("input[name='rack']").val();
          var position = Number($(this).find("input[name='position']").val());
          var result = update(name, type, rack, position, orientation);
          $(".toast-body").html();
          $(".toast-body").html(name + " Added to Rack "+ rack +".");
          $("#rack-toast").toast("show");
        } */ 
      }   
    });
  
  
}


function right_click(params) {

  
  var jQuery_1_6_2 = $.noConflict(true); 
    $('.right-click').bind("contextmenu",function(e){
      alert('Context Menu event has fired!');

      jQuery_1_6_2(function() {
        jQuery_1_6_2('.right-click').contextPopup({
          //console.log(jQuery_1_6_2(this)),
          title: 'My Popup Menu',
          items: [
            {label:'Details',     icon:'icons/shopping-basket.png',             action:function() { console.log(jQuery_1_6_2(this)); alert('clicked 1') } },
            {label:'Edit', icon:'icons/receipt-text.png',                action:function() { alert('clicked 2') } },
            {label:'Clone',     icon:'icons/book-open-list.png',              action:function() { alert('clicked 3') } },
            null, // divider
            {label:'Delete',         icon:'icons/application-monitor.png',         action:function() { alert('clicked 4') } },
            {label:'Power ON',        icon:'icons/bin-metal.png',                   action:function() { alert('clicked 5') } },
            {label:'Power OFF',         icon:'icons/magnifier-zoom-actual-equal.png', action:function() { alert('clicked 6') } },
            null, // divider
            {label:'Power Reset',       icon:'icons/application-table.png',           action:function() { alert('clicked 7') } },
            {label:'Power Status',      icon:'icons/cassette.png',                    action:function() { alert('clicked 8') } }
          ]
        });
      });


      return false;
   }); 

   
    var jQuery_1_6_2 = $.noConflict(true); // Resolving Conflict Between JQuery Versions - Sumit Sharma
    jQuery_1_6_2(function() {
      jQuery_1_6_2('.right-click').contextPopup({
        //console.log(jQuery_1_6_2(this)),
        title: 'My Popup Menu',
        items: [
          {label:'Details',     icon:'icons/shopping-basket.png',             action:function() { console.log(jQuery_1_6_2(this)); alert('clicked 1') } },
          {label:'Edit', icon:'icons/receipt-text.png',                action:function() { alert('clicked 2') } },
          {label:'Clone',     icon:'icons/book-open-list.png',              action:function() { alert('clicked 3') } },
          null, // divider
          {label:'Delete',         icon:'icons/application-monitor.png',         action:function() { alert('clicked 4') } },
          {label:'Power ON',        icon:'icons/bin-metal.png',                   action:function() { alert('clicked 5') } },
          {label:'Power OFF',         icon:'icons/magnifier-zoom-actual-equal.png', action:function() { alert('clicked 6') } },
          null, // divider
          {label:'Power Reset',       icon:'icons/application-table.png',           action:function() { alert('clicked 7') } },
          {label:'Power Status',      icon:'icons/cassette.png',                    action:function() { alert('clicked 8') } }
        ]
      });
    });

    
}