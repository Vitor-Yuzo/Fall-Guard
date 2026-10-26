import { Component, OnInit, inject } from '@angular/core';
import { DatePipe, PercentPipe } from '@angular/common';
import { FallsService, FallEvent } from './services/falls';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DatePipe, PercentPipe],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  private fallsService = inject(FallsService);

  falls: FallEvent[] = [];
  loading = true;
  errorMessage = '';

  ngOnInit(): void {
    this.loadFalls();
  }

  loadFalls(): void {
    this.loading = true;
    this.errorMessage = '';

    this.fallsService.getFalls().subscribe({
      next: (data) => {
        this.falls = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Erro ao carregar eventos:', error);
        this.errorMessage = 'Não foi possível carregar os eventos.';
        this.loading = false;
      }
    });
  }

  get totalFalls(): number {
    return this.falls.filter(fall => fall.evento === 'queda').length;
  }

  get fallsToday(): number {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const todayString = `${year}-${month}-${day}`;

    return this.falls.filter(fall =>
      fall.timestamp_evento.substring(0, 10) === todayString &&
      fall.evento === 'queda'
    ).length;
  }

  get lastFall(): FallEvent | null {
    return this.falls.length > 0 ? this.falls[0] : null;
  }

  get averageConfidence(): number | null {
    const values = this.falls
      .filter(fall => fall.confianca !== null)
      .map(fall => fall.confianca as number);

    if (values.length === 0) {
      return null;
    }

    return values.reduce((sum, value) => sum + value, 0) / values.length;
  }
}