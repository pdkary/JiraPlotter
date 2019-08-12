import { Component, OnInit } from '@angular/core';
import { CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { BoardService } from './board.service'
import { AnalysisWrapper } from 'src/data/AnalysisWrapper';
import {  Chart, Category, Trendlines, ScatterSeries, SplineSeries, Tooltip, LineSeries, TrendlineTypes} from '@syncfusion/ej2-charts';

Chart.Inject(Chart, ScatterSeries, SplineSeries, LineSeries, Tooltip, Trendlines, Category);

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  todo: String[];
  done = [];
  imageToShow: String | ArrayBuffer;
  isImageLoading = false;

  ngOnInit(): void {
    this.boardService.getBoards().subscribe(x => {
      this.todo = x;
    })
  }

  constructor(private boardService: BoardService) { }

  drop(event: CdkDragDrop<string[]>) {
    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      transferArrayItem(event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex);
    }
  }

  click() {
    this.isImageLoading = true;
    this.boardService.postBoards(this.done).subscribe(s => {
      this.loadChart(<AnalysisWrapper> s);
      this.isImageLoading = false;
    }, error => {
      this.isImageLoading = false;
      console.log(error);
    });
  }
  loadChart(wrapper: AnalysisWrapper){
    let data: Object[]=[];
    let point: Object;
    for(let i in wrapper.analysis.committed){
      point = {x: wrapper.analysis.committed[i],y:wrapper.analysis.completed[i]};
      data.push(point);
    }
    let chart = new Chart({
      primaryXAxis:{
        title:"Stories Committed",
      },
      primaryYAxis:{
        title:"Stories Completed",
      },
      tooltip:{enable:true},
      series:[{
        dataSource:data,
        xName:'x',
        yName:'y',
        name: 'Test',
        type: 'Scatter',
        trendlines:[{type: 'Linear'}]
      }],
      title: 'Stories Committed vs Stories Completed'
    },'#chart');
    this.isImageLoading=false;
  }
}
