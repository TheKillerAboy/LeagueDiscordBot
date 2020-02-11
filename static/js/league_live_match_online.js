function edit_field(partiId, fieldId, field, value){
    champion_panel = $(`#champion-${partiId}`)
    champion_panel.find(`.field-title.${fieldId}`).text(field);
    champion_panel.find(`.field-value.${fieldId}`).text(value);
}

function field_content(side,fieldId,field,value){
    return `<div class="field field-${side}">
                <div class="field-title white-font ${fieldId}">${field}</div>
                <div class="field-value grey-font ${fieldId}">${value}</div>
            </div>`
}
function enable_footer_cover(height){
    $('.champion-card').each(function(){
        footer_child = $(this).find(".footer-cover-disabled")
        footer_child.removeClass("footer-cover-disabled")
        footer_child.addClass("footer-cover")
        $(this).css("height",`${height}px`)
    })
}
function disable_footer_cover(){
    $('.champion-card').each(function(){
        footer_child = $(this).find(".footer-cover")
        footer_child.removeClass("footer-cover")
        footer_child.addClass("footer-cover-disabled")
        $(this).css("height",`auto`)
    })
}
function remove_field(partiId, fieldId){
    champion_panel = $(`#champion-${partiId}`)
}
function normalize_all_champion_panels(){
    max_high = 0
    $('.champion-card').each(function(){
        max_high = Math.max(max_high,$(this).height())
    })
    enable_footer_cover(max_high)
}

function add_field(partiId, fieldId, field, value){
    disable_footer_cover()
    champion_panel = $(`#champion-${partiId}`)
    amount = champion_panel.find('.field').length
    if(amount%2==0){
        champion_panel.find(".body").append(`
                            <div class="field-row">
                                ${field_content("left",fieldId,field,value)}
                                <div class="field-clear"></div>
                            </div>`)
    }
    else{
        console.log(champion_panel.find(".field-row").last())
        champion_panel.find(".field-row").last().find('.field-clear').before(field_content("right",fieldId,field,value))
    }
    normalize_all_champion_panels()
}

function write_field(partiId, fieldId, field, value){
    champion_panel = $(`#champion-${partiId}`)
    if(!champion_panel.find(`.field-title.${fieldId}`).length){
        add_field(partiId,fieldId,field,value)
    }
    else{
        edit_field(partiId,fieldId,field,value)
    }
}
function set_header_info(partiId,icon, name, lvl, hours){
    champion_panel = $(`#champion-${partiId}`)
    champion_panel.find(".pfp>img").attr("src",icon)
    champion_panel.find(".name").text(name)
    champion_panel.find(".lvl").text(lvl)
    champion_panel.find(".time-wasted").text(hours)
}
function set_footer_info(partiId,icon, name, lvl, pts, spell1, spell2){
    champion_panel = $(`#champion-${partiId}`)
    champion_panel.find(".champion-pfp>img").attr("src",icon)
    champion_panel.find(".champion-name").text(name)
    champion_panel.find(".champion-lvl").text(lvl)
    champion_panel.find(".champion-points").text(pts)
    champion_panel.find(".champion-skill-1>img").attr("src",spell1)
    champion_panel.find(".champion-skill-2>img").attr("src",spell2)
}
function set_loading_info(partiId,perc){
    champion_panel = $(`#champion-${partiId}`)
    champion_panel.find(".loading-bar-top").css('width',`${perc}%`)
}