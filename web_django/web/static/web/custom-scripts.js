$(document).on('submit', '#period', function(event){
    event.preventDefault();
    let url = $(this).attr('action'),
	data = $(this).serialize();
    $.post(url, data, function(response){
	updateData(
	    response.account_balance,
	    response.pnl,
	    response.pnl_index,
	    response.pnl_percentage,
 	    response.start_period,
 	    response.end_period
	)
    })
})
let updateData = (accountBalance, pnl, pnlIndex, pnlPercentage, start, end) => {
    $('#accountBalance').text(accountBalance);
    $('#pnl').text(pnl.slice(0, pnl.indexOf('.') + 2));
    $('#pnlIndex').text(pnlIndex.slice(0, pnlIndex.indexOf('.') + 5));
    $('#pnlPercentage').text(pnlPercentage);
    $('#id_start').val(start.substring(0, start.lastIndexOf(':')));
    $('#id_end').val(end.substring(0, end.lastIndexOf(':')));
    let statusIcons = $('.panel-left')
	isGreen = Number.parseFloat(pnlIndex) > 1;
    for (let i = 1; i < statusIcons.length; i++) {
        statusIcons[i].classList.remove('red');
	statusIcons[i].classList.remove('green');
	statusIcons[i].classList.add(isGreen ? 'green' : 'red');
    }
};
