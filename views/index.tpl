% rebase('base.tpl', title='Office 365 health')
<div class="card-columns">
  %for status in statuses:
  <div class="card" data-statusdate="{{status['StatusDate']}}" data-workload="{{status['Workload']}}">
    <div class="card-body">
      <p class="card-text">{{status['WorkloadDisplayName']}}</p>
      <p class="card-text">
        <small class="text-muted">
          <a>{{len(status['IncidentIds'])}}</a>
        </small>
      </p>
    </div>
  </div>
  %end
</div>