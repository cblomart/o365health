interval=10000
timeout=4000

function poll() {
  $.ajax({
    url: "/api/status",
    timeout: timeout
  }).done(function(workloads) {
    (workloads).forEach(workload => {
      e = $("div.card[data-workload=" + workload.Workload +"]")
      if (e.length > 0) {
        console.log("found " + workload.Workload)
      } else {
        $("div.card[data-template=true]")
          .clone()
          .attr('data-template',false)
          .attr('data-workload',workload.Workload)
          .attr('data-statustime',workload.StatusTime)
          .attr('data-status',workload.Status)
          .find('#description').text(workload.WorkloadDisplayName).end()
          .find('#incidents').text(workload.Incidents).end()
          .find
          .appendTo("div.card-columns")
      }
      $("div.card[data-template=false]").attr("hidden",false)
      $("#loadworkloads").attr("hidden",true)
    });
  });
  setTimeout(poll,interval);
}

poll();