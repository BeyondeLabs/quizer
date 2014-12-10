$(document).ready(
	function(){
		
		//form manupulation for twitter bootstrap
		$("input[type=submit]").addClass("btn btn-inverse");
		
		$tooltip = $("input[type=text],textarea,a"); 
		$tooltip.each(
			function(index){
				$(this).attr('title',$(this).attr('placeholder'));
			}
		)
		
		$tooltip.on("focus hover",function(){
			$(this).tooltip('show');
		});
		
		$("a#startattempt").click(function(e){
			e.preventDefault();
			$this = $(this).hide();
			$this.parent().find("a#retake").show();
			$this.parent().find("#score").html("Current Score: <score>0.0</score>");
			
			var url = "/explore/revision/attempt/first";
			
			var post_data = {
				'rev_key':$this.attr('data-rev')
			};
			$.post(url,post_data,function(data){
				// console.log(data);
				$this.parent().attr('data-akey',data);
			});

			$("ol.questions").show();
		});
		
		$("a#retake").click(function(e){
			e.preventDefault();
			var $this = $(this);
			$this.parent().find("#score").html("Current Score: <score>0.0</score>");
			
			var url = "/explore/revision/attempt/first";
			
			var post_data = {
				'rev_key':$this.attr('data-rev')
			};
			$.post(url,post_data,function(data){
				console.log(data);
				$this.parent().attr('data-akey',data);
			});
		});
		
		$("ul.answers input[type=radio]").click(
			function(){
				var akey = $("#attempt").attr('data-akey');
				if(akey != ''){
					$this = $(this);
					$this.parent().parent().find("span.ans").remove();
					//record the first answer chosen --> server side validation, can be done on client-side too
					var post_data = {
						'ans_key':$this.attr('data-key'),
						'att_key':akey,
						'q_key':$this.attr('name'),
						'q_count':$("#qcount").attr('data')
					};
					var url = "/explore/revision/attempt/answer";
					$.post(url,post_data,function(data){
						// console.log(data);
						if(data>0){
							$("#score score").text(data);
						}
					});
					
					if($this.attr('data-c')=="True"){
						$(this).next().after("<span class='ans correct'> <i class='icon-ok'></i> Correct</span>");
					}else{
						$(this).next().after("<span class='ans wrong'> <i class='icon-remove'></i> Wrong</span>");
					}
				}
			}
		);
		
		$(".discussion").hide();
		
		$("a.toggle-discussion").click(function(e){
			$this = $(this);
			$this.parent().next().slideToggle();
			e.preventDefault();
		});
		
		//ajax
		$('.answers a.del').on('click',function(e){
			var $this = $(this);
			console.log($this);
			$.post("/revision/questions/ans/del/"+$this.attr('ans-key'),{},function(data){
				$this.parent().remove();
			});
			e.preventDefault();
		});
		
		$('.questions a.del').on('click',function(e){
			var $this = $(this);
			console.log($this);
			$.post("/revision/questions/del/"+$this.attr('qs-key'),{},function(data){
				$this.parent().remove();
			});
			e.preventDefault();
		});
		
		$('.question-comm-ent-form').submit(function(e){
			e.preventDefault();
			var $form = $(this),
			url = $form.attr('action'),
			post_data = $form.serialize();
			
			$comment = $form.find("textarea");
			
			var comment = $comment.val();
	
			
			//console.log(post_data);
			// $form.parent().find("p:last").after("<p>"+comment+" - {{sess_user.user.name}}<p>");
			
			$.post(url,post_data,function(data){
				// console.log(data);
			});
			
			
		});
		
		$('.date').datepicker();
	}
);


