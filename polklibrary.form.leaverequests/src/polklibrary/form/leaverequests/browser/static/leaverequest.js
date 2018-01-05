
var LeaveRequest = {
    
    TimeSlotCloneable : null,
    IsAcademicStaff : false,
    
    Construct : function() {
        this.PopulateFields();
        this.TimeSlotCloneable = this.MakeTimePicker();
        this.GetStaffStatus();
        this.Setup();
    },
    
    PopulateFields : function() {
        if ($.trim($('#form-widgets-title').val()) == '') {
            var name = $('#leave-request-injection').attr('data-name');
            $('#form-widgets-title').val(name);
        }
        if ($.trim($('#form-widgets-email').val()) == '') {
            var email = $('#leave-request-injection').attr('data-email');
            $('#form-widgets-email').val(email);
        }
    },
    
    GetStaffStatus : function() {
        var url = $('body').attr('data-portal-url') + '/get_stafftype?nocache=' + new Date().getTime();
        $.getJSON(url, function(response){
            LeaveRequest.IsAcademicStaff = response.is_academic_staff;
            if (LeaveRequest.IsAcademicStaff){
                $('input[type="number"]').attr({
                    'step':'4',
                    'min':'0',
                    'max':'8',
                    'value':'4'
                });
            }
        });
    },
    
    Setup : function() {
        var label = $('<label>').html('Time Off');
        var div = $('<div>').attr('id','form-timeslot-request').html(label);
        
        var txt = $('#form-widgets-timeoff').text();
        if (txt == '')
            $(div).append(this.MakeRow(false));
        else {
            var rows = txt.split('\n');
            for(var i = 0; i < rows.length; i++){
                var data = rows[i].split('|');
                $(div).append(this.MakeRow(false,data[0],data[1],data[2],data[3],data[4]));
            }
        }
        
        var btn = $('<input>').addClass('timeslot-add').attr({'type': 'button', 'value': 'Add'}).on('click', function(){
            $(this).before( LeaveRequest.MakeRow(true) );
        });
        $(div).append(btn);
        $(div).append('<div class="help">(Note: Time taken is how many hours you will submit in HRS. Out from/to is when you will actually be gone that day.  If you plan on being gone during lunch, make sure to include it in the out from/to)</div>');
        
        $('#formfield-form-widgets-timeoff').before(div);
        
    },
    
    
    Rewrite : function(){
        $('#form-widgets-timeoff').text('');
        $('.timeslot-row').each(function(){
            var selectdate = $(this).find('.datepick').val();
            var leavetype = $(this).find('.leavepick option:selected').val();
            var duration = $(this).find('.durationpick').val();
            var starttime = $(this).find('.timepick.start option:selected').val();
            var endtime = $(this).find('.timepick.end option:selected').val();
            
            var txt = $('#form-widgets-timeoff').text();
            txt = txt + selectdate + '|' + leavetype + '|' + duration + '|' + starttime + '|' + endtime + '\n';
            $('#form-widgets-timeoff').text(txt);
        });
    },
    
    MakeRow : function(delete_option, data_date, data_leave, data_duration, data_start, data_end){
        var div = $('<div>').addClass('timeslot-row');
        
        var leavepick = this.MakeLeaveType();
        $(leavepick).on('change', function(){
            LeaveRequest.Rewrite();
        });
        if (data_leave != null)
            $(leavepick).find('option[value="' + data_leave + '"]').attr('selected', true);
        
        
        var datepick = $('<input>').attr('type','text')
                                   .addClass('datepick')
                                   .datepicker({ 'beforeShowDay': $.datepicker.noWeekends })
                                   .on('change', function(){
                                        var d = $(this).val();
                                        if (d == '')
                                             $(this).val("11/19/1985");
                                        LeaveRequest.Rewrite();
                                    });
                                    
        if (data_date != null)
            $(datepick).datepicker("setDate", new Date(data_date));
        else
            $(datepick).datepicker("setDate", new Date());
        
        var duration = this.MakeDurationPick();
        if (data_duration != null)
            $(duration).val(data_duration);
        $(duration).on('change', function(){
            var v = $(this).val();
            if (LeaveRequest.IsAcademicStaff == true && (v != 8 || v != 4)) {
                alert('Academic Staff can only takes time off in increments of 4 hours');
                if (v < 4)
                    $(this).val(4);
                if (v > 4)
                    $(this).val(8);
            }
            else
            {
                if (v < 0)
                    $(this).val(0);
                if (v > 8)
                    $(this).val(8);
            }
            LeaveRequest.Rewrite();
        });
        
        var start = $(this.TimeSlotCloneable).clone(true);
        $(start).addClass('start').on('change', function(){
            LeaveRequest.Rewrite();
        });
        if (data_start != null)
            $(start).find('option[value="' + data_start + '"]').attr('selected', true);
        
        
        var end = $(this.TimeSlotCloneable).clone(true);
        $(end).addClass('end').on('change', function(){
            LeaveRequest.Rewrite();
        });
        
        if (data_end != null)
            $(end).find('option[value="' + data_end + '"]').attr('selected', true);
        
        var btn = $('<input>').addClass('destructive').attr({'type': 'button', 'value': 'Delete'}).on('click', function(){
            $(div).remove();
        });
        
        $(div).append(datepick)
              .append(leavepick)
              .append('<span> time taken </span>')
              .append(duration)
              .append('<span> out from </span>')
              .append(start).append('<span> to </span>')
              .append(end);
        if (delete_option) 
            $(div).append(btn);
            
        return div;
    },
    
    
    MakeDurationPick : function(){
        var step = 0.25;
        var min = 0;
        var max = 8;
        var value = 1;
        if(LeaveRequest.IsAcademicStaff){
            step = 4;
            min = 0;
            max = 8;
            value = 4; 
        }
        var durationpick = $('<input>').attr({'type':'number','step':step,'min':min,'max':max,'value':value}).addClass('durationpick');
        return durationpick;
    },
    
    MakeLeaveType : function(){
        var leavepick = $('<select>').addClass('leavepick');
        $(leavepick).append( $('<option>').val('VA').html('Vacation') );
        $(leavepick).append( $('<option>').val('SL').html('Sick Leave') );
        $(leavepick).append( $('<option>').val('FH').html('Floating/Legal Holiday') );
        $(leavepick).append( $('<option>').val('CT').html('Comp Time (University Staff Only)') );
        $(leavepick).append( $('<option>').val('O').html('Other') );
        return leavepick;
    },
    
    
    
    
    // Only run once at load
    MakeTimePicker : function(){
        var timepick = $('<select>').addClass('timepick');
        $(timepick).append( $('<option>').val('12:00 am').html('12:00 am') );
        $(timepick).append( $('<option>').val('12:15 am').html('12:15 am') );
        $(timepick).append( $('<option>').val('12:30 am').html('12:30 am') );
        $(timepick).append( $('<option>').val('12:45 am').html('12:45 am') );
        for(var i = 1; i < 12; i++)
            for(var j = 0; j < 59; j+=15) {
                k = j + '';
                if (j == 0) k = '00';
                $(timepick).append( $('<option>').attr('selected', i == 8 && j == 0).val(i + ':' + k + ' am').html(i + ':' + k + ' am') );
            }
            
        $(timepick).append( $('<option>').val('12:00 pm').html('12:00 pm') );
        $(timepick).append( $('<option>').val('12:15 pm').html('12:15 pm') );
        $(timepick).append( $('<option>').val('12:30 pm').html('12:30 pm') );
        $(timepick).append( $('<option>').val('12:45 pm').html('12:45 pm') );
        for(var i = 1; i < 12; i++)
            for(var j = 0; j < 59; j+=15) {
                k = j + '';
                if (j == 0) k = '00';
                $(timepick).append( $('<option>').val(i + ':' + k + ' pm').html(i + ':' + k + ' pm') );
            }
        return timepick;
    }
    
    
    
}







$(document).ready(function(){
    
    LeaveRequest.Construct();
});